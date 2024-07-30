from typing import Optional

import json
import logging
import os
from pathlib import Path

import pandas as pd
import reflex as rx
from feast import FeatureView, FileSource
from feast.data_format import ParquetFormat
from feast.data_source import PushSource
from feast.feature_store import FeatureStore
from feast.field import Field
from feast.repo_config import RepoConfig
from feast.repo_operations import _prepare_registry_and_repo, apply_total_with_repo_instance
from feast.types import Array, Float32
from sqlmodel import select

from aita_lab.states.base import BaseState
from aita_lab.states.datasource import DataSourceState


class VectorStoreConfig(rx.Base):
    """
    VectorStoreConfig is a model that holds the configuration for storying the registry data.
    It will be used by feast to apply the feature store.
    """

    registry_type: str
    path: str


def get_vector_store_config():
    rx_config = rx.config.get_config()
    if "vector_store_config" in rx_config:
        return rx_config["vector_store_config"]
    else:

        # default config
        return VectorStoreConfig(**{
            "registry_type": "file",
            "path": "data/vector.db"
        })


class VectorStore(rx.Model, table=True):
    project_name: str
    online_store_type: str
    offline_store_type: Optional[str]
    online_store_configs: Optional[str]
    offline_store_configs: Optional[str]


class FeastFeatureView(rx.Model):
    name: str
    feature: str
    entities: Optional[str] = ""
    source: Optional[str] = ""


class VectorStoreState(BaseState):
    projects: list[VectorStore] = []

    project_name: str
    online_store_type: str
    offline_store_type: Optional[str] = ""
    online_store_configs: Optional[dict[str, str]] = {}
    offline_store_configs: Optional[dict[str, str]] = {}

    feature_view_name: str
    feature_name: str
    feature_entities: Optional[str] = None
    data_source_type: Optional[str] = ""

    vector_feature_views: list[FeastFeatureView] = []

    store_dialog_open: bool = False
    feature_dialog_open: bool = False

    _fs: Optional[FeatureStore] = None

    files: list[str] = []
    vector_store_config: VectorStoreConfig = get_vector_store_config()

    def set_online_store_type(self, ds: str):
        self.online_store_type = ds
        ds = DataSourceState.get_datasource_by_name(ds)
        configs = DataSourceState.get_configs(ds)
        if "connection_url" in configs:
            configs = {
                "path": configs["connection_url"],
            }
        self.online_store_configs = {
            "type": self.online_store_type,
            **configs,
        }
        logging.info(f"Online store type set to {self.online_store_type} with configs {self.online_store_configs}")

    def open_feature_dialog(self):
        self.feature_dialog_open = not self.feature_dialog_open

    def toggle_store_dialog(self):
        self.store_dialog_open = not self.store_dialog_open

    def set_project(self, project_name: str):
        self.project_name = project_name
        self._load_project()

    def _load_project(self):
        project = next(
            (project for project in self.projects if project.project_name == self.project_name),
            None,
        )
        if project:
            repo_config = self._build_feast_repo_config(
                project_name=project.project_name,
                online_store_type=project.online_store_type,
                online_store_configs=json.loads(project.online_store_configs if project.online_store_configs else "{}"),
                offline_store_type=project.offline_store_type,
                offline_store_configs=json.loads(project.offline_store_configs if project.offline_store_configs else "{}"),
            )
            self._fs = FeatureStore(config=repo_config)
            self.vector_feature_views = self._get_feature_views()

    def _build_feast_repo_config(
            self,
            project_name,
            online_store_type: str,
            online_store_configs: dict[str, str],
            offline_store_type: Optional[str] = None,
            offline_store_configs: dict[str, str] = None,
    ):
        return RepoConfig(
            project=project_name,
            registry={
                "type": self.vector_store_config.registry_type,
                "path": self.vector_store_config.path,
            },
            provider="local",
            online_config={
                "type": online_store_type,
                **online_store_configs,
            },
            offline_config={
                "type": offline_store_type,
                **(offline_store_configs if offline_store_configs else {}),
            },
            entity_key_serialization_version=3,
        )

    def create_store(self):
        logging.info("Creating feature store with the following configurations:")

        repo_config = self._build_feast_repo_config(
            project_name=self.project_name,
            online_store_type=self.online_store_type,
            online_store_configs=self.online_store_configs,
            offline_store_type=self.offline_store_type,
            offline_store_configs=self.offline_store_configs,
        )
        repo_path = Path(os.path.join(Path.cwd(), "data"))
        try:
            project, registry, repo, store = _prepare_registry_and_repo(repo_config, repo_path)
            apply_total_with_repo_instance(store, project, registry, repo, True)
            self._fs = FeatureStore(config=repo_config)

            logging.info("Feature store applied successfully.")
        except Exception as e:
            logging.error(f"Error creating feature store: {e}")
            raise e
        finally:
            # save the project to the database
            with rx.session() as session:
                session.add(
                    VectorStore(
                        project_name=self.project_name,
                        online_store_type=self.online_store_type,
                        offline_store_type=self.offline_store_type,
                        online_store_configs=self.online_store_configs,
                        offline_store_configs=self.offline_store_configs,
                    )
                )
                session.commit()
            self.toggle_store_dialog()

    def _create_feature_schema(self):
        return [Field(name=self.feature_name, dtype=Array(Float32))]

    def _create_feature_source(self):
        return PushSource(
            name=self.feature_view_name,  # feature view name is used to reference the source
            batch_source=FileSource(
                file_format=ParquetFormat(),
                path="data/feature.parquet",
                timestamp_field="event_timestamp",
            ),
        )

    def create_vector_feature(self):
        self._fs.apply(
            FeatureView(
                name=self.feature_view_name,
                entities=self.feature_entities if self.feature_entities else [],
                schema=self._create_feature_schema(),
                source=self._create_feature_source(),
            )
        )
        logging.info(f"Feature View {self.feature_view_name} created")
        self.open_feature_dialog()

    def _get_feature_views(self) -> list[FeastFeatureView]:
        vector_feature_views = []
        for feature_view in self._fs.list_feature_views():
            feature_spec = self._fs.get_feature_view(feature_view.name)
            vector_feature_views.append(
                FeastFeatureView(
                    name=feature_spec.name,
                    entities=", ".join([entity.name for entity in feature_spec.entity_columns]),
                    feature=", ".join([feature.name for feature in feature_spec.features]),
                    source=feature_spec.stream_source.name,
                )
            )
        return vector_feature_views

    def load_store(self):
        with rx.session() as session:
            self.projects = session.exec(select(VectorStore)).all()

        self._load_project()

        logging.info("Feature store loaded")

    def push_source_to_feature(self, feature_view: dict):
        (name, entities, feature, source) = (
            feature_view["name"],
            feature_view["entities"],
            feature_view["feature"],
            feature_view["source"],
        )
        root_dir = rx.get_upload_dir()
        source_dir = f"{root_dir}/{source}/"
        feature_df = pd.read_parquet(source_dir)
        if feature_df.empty:
            logging.error(f"Error loading feature: {source} is empty")
            return
        if not all(col in feature_df.columns for col in ["event_timestamp", feature, entities]):
            logging.error(
                f"Error loading feature: {source} is missing required columns: event_timestamp, {feature}, {entities}"
            )
            return

        try:
            self._fs.push(source, feature_df)
            logging.info(f"Source {source} pushed to feature.")
        except Exception as e:
            logging.error(f"Error loading feature: {e}")
            raise e

    def _retrieve_vector_features(self, feature: str, query, top_k: int = 3) -> dict:
        logging.info(f"Retrieving online documents for {feature} with query {query}")
        response = self._fs.retrieve_online_documents(feature=feature, query=query, top_k=top_k)
        return response.to_dict()

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

    def on_load(self) -> None:
        self.load_store()
