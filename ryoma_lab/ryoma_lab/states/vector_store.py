import datetime
import logging
import os
import pathlib
from pathlib import Path
from typing import Optional

import pandas as pd
import reflex as rx
from feast import FeatureView, FileSource
from feast.data_format import ParquetFormat
from feast.data_source import DataSource as FeastDataSource
from feast.data_source import PushSource
from feast.feature_store import FeatureStore
from feast.field import Field
from feast.repo_operations import (
    _prepare_registry_and_repo,
    apply_total_with_repo_instance,
)
from feast.types import Array, Float32
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from ryoma.agent.embedding import EmbeddingAgent
from ryoma.agent.factory import AgentFactory
from ryoma_lab.apis.datasource import get_datasource_by_name, get_datasource_configs
from ryoma_lab.apis.vector_store import get_feature_stores
from ryoma_lab.models.vector_store import FeastFeatureView, VectorStore
from ryoma_lab.services.vector_store import (
    build_feast_repo_config,
    get_feast_datasource_by_name,
    get_feature_store,
    get_feature_views,
)
from ryoma_lab.states.base import BaseState
from ryoma_lab.states.datasource import DataSource, DataSourceState


class VectorStoreState(BaseState):
    projects: list[VectorStore] = []
    project: Optional[VectorStore] = None

    project_name: str
    online_store: str
    offline_store: Optional[str] = ""
    offline_store_source: Optional[DataSource] = None
    online_store_configs: Optional[dict[str, str]] = {}
    offline_store_configs: Optional[dict[str, str]] = {}

    feature_view_name: str
    feature_name: str
    feature_entities: Optional[str] = None
    feature_datasource: Optional[str] = None

    _current_fs: Optional[FeatureStore] = None
    current_feature_views: list[FeastFeatureView] = []

    create_store_dialog_open: bool = False
    create_feature_dialog_open: bool = False
    materialize_feature_dialog_open: bool = False

    files: list[str] = []
    feature_source_configs: dict[str, str] = {}

    materialize_embedding_model: Optional[str] = None
    materialize_embedding_model_configs: Optional[str] = None

    def set_feature_source_config(self, key: str, value: str):
        self.feature_source_configs[key] = value

    def _get_datasource_configs(self, ds: str) -> dict[str, str]:
        ds = get_datasource_by_name(ds)
        configs = get_datasource_configs(ds)
        if "connection_url" in configs:
            configs = {
                "path": configs["connection_url"],
            }
        return configs

    def set_online_store(self, ds: str):
        self.online_store = ds
        configs = self._get_datasource_configs(ds)
        self.online_store_configs = {
            "type": self.online_store,
            **configs,
        }
        logging.info(
            f"Online store type set to {self.online_store} with configs {self.online_store_configs}"
        )

    def set_offline_store(self, ds: str):
        self.offline_store = ds
        configs = self._get_datasource_configs(ds)
        self.offline_store_configs = {
            "type": self.offline_store,
            **configs,
        }
        logging.info(
            f"Offline store type set to {self.offline_store} with configs {self.offline_store_configs}"
        )

    def toggle_create_feature_dialog(self):
        self.create_feature_dialog_open = not self.create_feature_dialog_open

    def toggle_create_store_dialog(self):
        self.create_store_dialog_open = not self.create_store_dialog_open

    def toggle_materialize_feature_dialog(self):
        self.materialize_feature_dialog_open = not self.materialize_feature_dialog_open

    def set_project(self, project_name: str):
        self.project_name = project_name
        self._reload_project(self.project_name)

    def _reload_project(self, project_name: Optional[str] = None):
        project = None
        if project_name:
            project = next(
                (
                    project
                    for project in self.projects
                    if project.project_name == project_name
                ),
                None,
            )
        elif self.projects:
            project = self.projects[0]
        if project:
            self.project = project
            self._current_fs = get_feature_store(project, self.vector_store_config)
            self.current_feature_views = get_feature_views(self._current_fs)

    def create_store(self):
        repo_config_input = {
            "project_name": self.project_name,
            "vector_store_config": self.vector_store_config,
            "online_store": self.online_store,
            "online_store_configs": dict(self.online_store_configs),
            "offline_store": self.offline_store,
            "offline_store_configs": dict(self.offline_store_configs),
        }
        logging.info(
            "Creating feature store with the following configurations: %s",
            repo_config_input,
        )

        repo_config = build_feast_repo_config(**repo_config_input)
        repo_path = Path(os.path.join(Path.cwd(), "data"))
        try:
            project, registry, repo, store = _prepare_registry_and_repo(
                repo_config, repo_path
            )
            apply_total_with_repo_instance(store, project, registry, repo, True)
            self._current_fs = FeatureStore(config=repo_config)

            logging.info("Feature store applied successfully.")

            # save the project to the database
            with rx.session() as session:
                session.add(
                    VectorStore(
                        project_name=self.project_name,
                        online_store=self.online_store,
                        offline_store=self.offline_store,
                        online_store_configs=str(self.online_store_configs),
                        offline_store_configs=str(self.offline_store_configs),
                    )
                )
                session.commit()
            self.load_store()
        except Exception as e:
            logging.error(f"Error creating feature store: {e}")
            raise e
        finally:
            self.toggle_create_store_dialog()

    def _create_feature_schema(self):
        return [Field(name=self.feature_name, dtype=Array(Float32))]

    def _create_feature_source(self) -> FeastDataSource:
        if self.feature_datasource == "files":
            return PushSource(
                name="\n".join(
                    self.files
                ),  # feature view name is used to reference the source
                batch_source=FileSource(
                    file_format=ParquetFormat(),
                    path="data/feature.parquet",
                    timestamp_field="event_timestamp",
                ),
            )
        else:
            ds = get_datasource_by_name(self.feature_datasource)
            datasource_cls = get_feast_datasource_by_name(ds.datasource)
            if datasource_cls:
                return datasource_cls(
                    name=self.feature_view_name, **self.feature_source_configs
                )
            else:
                logging.error(
                    f"Data source for {self.feature_datasource} not supported"
                )
            raise ValueError(f"Data source for {self.feature_datasource} not supported")

    def _create_additional_tags(self) -> dict[str, str]:
        if self.feature_datasource == "files":
            return {"push_source_type": self._get_file_type(self.files[0])}

    def create_vector_feature(self):
        self._current_fs.apply(
            FeatureView(
                name=self.feature_view_name,
                entities=self.feature_entities if self.feature_entities else [],
                schema=self._create_feature_schema(),
                source=self._create_feature_source(),
                tags=self._create_additional_tags(),
            )
        )
        logging.info(f"Feature View {self.feature_view_name} created")
        self._reload_project()
        self.toggle_create_feature_dialog()

    def load_store(self):
        self.projects = get_feature_stores()
        self._reload_project()

        logging.info("Feature store loaded")

    def materialize_feature(self, feature_view: FeastFeatureView):
        logging.info(f"Loading feature view {feature_view}")
        if feature_view["source_type"] != "PushSource":
            self._materialize_offline_feature_view(feature_view)
            return

        root_dir = rx.get_upload_dir()
        source_dir = f"{root_dir}/{feature_view['name']}/{feature_view['source']}"
        push_source_type = feature_view["push_source_type"]

        if push_source_type in ["parquet", "csv", "json", "txt"]:
            self._process_file_source(feature_view, source_dir, push_source_type)
        elif push_source_type == "pdf":
            self._process_pdf_source(feature_view, source_dir)
        else:
            logging.error(f"Unsupported source type: {push_source_type}")

    def _materialize_offline_feature_view(self, feature_view: FeastFeatureView):
        logging.info(f"Materializing offline feature view {feature_view}")
        self._current_fs.materialize_incremental(
            datetime.datetime.now(), [feature_view["name"]]
        )

    def _process_file_source(
        self, feature_view: FeastFeatureView, source_dir: str, file_type: str
    ):
        try:
            feature_df = self._load_feature_dataframe(source_dir, file_type)
            if self.materialize_embedding_model:
                feature_df = self._apply_embedding(feature_df)
            self._validate_feature_dataframe(feature_df, feature_view)
            self._current_fs.push(feature_view["source"], feature_df)
            logging.info(f"Source {feature_view['source']} pushed to feature.")
        except Exception as e:
            logging.error(f"Error processing file source: {e}")
            raise e

    def _process_pdf_source(self, feature_view, source_dir):
        try:
            docs = PyPDFLoader(source_dir).load()
            if self.materialize_embedding_model:
                embedding_agent = self._create_embedding_agent()
                self._process_pdf_document(docs, embedding_agent, feature_view)
        except Exception as e:
            logging.error(f"Error processing PDF source: {e}")
            raise e

    def _load_feature_dataframe(self, source_dir, file_type):
        if file_type == "parquet":
            return pd.read_parquet(source_dir)
        # Add support for other file types (csv, json, txt) if needed
        raise ValueError(f"Unsupported file type: {file_type}")

    def _create_embedding_agent(
        self,
    ) -> EmbeddingAgent:
        return AgentFactory.create_agent(
            "embedding",
            model=self.materialize_embedding_model,
            model_parameters=self.materialize_embedding_model_configs,
        )

    def _apply_embedding(self, feature_df):
        logging.info("Run embedding before materializing feature")
        embedding_agent = self._create_embedding_agent()

        feature_df["feature"] = feature_df["feature"].apply(
            lambda x: embedding_agent.embed_query(x) if isinstance(x, str) else x
        )
        return feature_df

    def _validate_feature_dataframe(self, feature_df, feature_view):
        required_columns = [
            "event_timestamp",
            feature_view["feature"],
            feature_view["entities"],
        ]
        if feature_df.empty:
            logging.error(f"Error loading feature: {feature_view['source']} is empty")
            raise ValueError("Feature DataFrame is empty")
        if not all(col in feature_df.columns for col in required_columns):
            missing_columns = [
                col for col in required_columns if col not in feature_df.columns
            ]
            logging.error(
                f"Error loading feature: {feature_view['source']} is missing required columns: {', '.join(missing_columns)}"
            )
            raise ValueError("Missing required columns")

    def _process_pdf_document(
        self,
        docs: list[Document],
        embedding_agent: EmbeddingAgent,
        feature_view: FeastFeatureView,
    ):
        embedded_data = embedding_agent.embed_documents(docs)
        inputs = {
            "event_timestamp": [datetime.datetime.now()] * len(embedded_data),
            feature_view["feature"]: embedded_data,
            feature_view["entities"]: [""] * len(embedded_data),
        }
        self._current_fs.write_to_online_store(
            feature_view_name=feature_view["name"], inputs=inputs
        )

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle the upload of file(s).

        Args:
            files: The uploaded files.
        """
        root_dir = rx.get_upload_dir()
        source_dir = f"{root_dir}/{self.feature_view_name}"
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)

        for file in files:
            upload_data = await file.read()
            outfile = Path(f"{source_dir}/{file.filename}")

            # Save the file.
            with outfile.open("wb") as file_object:
                file_object.write(upload_data)

            # Update the files var.
            self.files.append(file.filename)

    def _get_file_type(self, file: str) -> str:
        supported_file_types = {
            ".txt": "txt",
            ".csv": "csv",
            ".parquet": "parquet",
            ".json": "json",
            ".html": "html",
            ".pdf": "pdf",
        }
        file_type = pathlib.Path(file).suffix
        return supported_file_types.get(file_type, "txt")

    def delete_project(self, project_name):
        with rx.session() as session:
            session.query(VectorStore).filter_by(project_name=project_name).delete()
            session.commit()
        self.load_store()

    def on_load(self) -> None:
        self.load_store()
