from typing import Optional

import json
import logging
import os
from enum import Enum
from pathlib import Path

import pandas as pd
import reflex as rx
from feast import BigQuerySource, FeatureView, FileSource, RedshiftSource, SnowflakeSource
from feast.data_format import ParquetFormat
from feast.data_source import DataSource as FeastDataSource
from feast.data_source import PushSource
from feast.feature_store import FeatureStore
from feast.field import Field
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
    PostgreSQLSource,
)
from feast.repo_config import RepoConfig
from feast.repo_operations import _prepare_registry_and_repo, apply_total_with_repo_instance
from feast.types import Array, Float32
from sqlmodel import select

from aita_lab.states.base import BaseState
from aita_lab.states.datasource import DataSource, DataSourceState

FEAST_DATASOURCE_MAP = {
    "postgresql": PostgreSQLSource,
    "snowflake": SnowflakeSource,
    "bigquery": BigQuerySource,
    "redshift": RedshiftSource,
}


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
        return VectorStoreConfig(**{"registry_type": "file", "path": "data/vector.db"})


class VectorStore(rx.Model, table=True):
    project_name: str
    online_store: str
    offline_store: Optional[str]
    online_store_configs: Optional[str]
    offline_store_configs: Optional[str]


class FeastFeatureView(rx.Model):
    name: str
    feature: str
    entities: Optional[str] = ""
    source: Optional[str] = ""


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

    vector_feature_views: list[FeastFeatureView] = []

    store_dialog_open: bool = False
    feature_dialog_open: bool = False

    _fs: Optional[FeatureStore] = None

    files: list[str] = []
    vector_store_config: VectorStoreConfig = get_vector_store_config()
    feature_source_configs: dict[str, str] = {}

    def set_feature_source_config(self, key: str, value: str):
        self.feature_source_configs[key] = value

    def _get_datasource_configs(self, ds: str) -> dict[str, str]:
        ds = DataSourceState.get_datasource_by_name(ds)
        configs = DataSourceState.get_configs(ds)
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

    def open_feature_dialog(self):
        self.feature_dialog_open = not self.feature_dialog_open

    def toggle_store_dialog(self):
        self.store_dialog_open = not self.store_dialog_open

    def set_project(self, project_name: str):
        self.project_name = project_name
        self._reload_project(self.project_name)

    def _reload_project(self, project_name: Optional[str] = None):
        project = None
        if project_name:
            project = next(
                (project for project in self.projects if project.project_name == project_name),
                None,
            )
        elif self.projects:
            project = self.projects[0]
        if project:
            self.project = project
            repo_config = self._build_feast_repo_config(
                project_name=project.project_name,
                online_store=project.online_store,
                online_store_configs=json.loads(
                    project.online_store_configs if project.online_store_configs else "{}"
                ),
                offline_store=project.offline_store,
                offline_store_configs=json.loads(
                    project.offline_store_configs if project.offline_store_configs else "{}"
                ),
            )
            self._fs = FeatureStore(config=repo_config)
            self.vector_feature_views = self._get_feature_views()

    def _build_feast_repo_config(
        self,
        project_name,
        online_store: str,
        online_store_configs: dict[str, str],
        offline_store: Optional[str] = None,
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
                "type": online_store,
                **online_store_configs,
            },
            offline_config={
                "type": offline_store,
                **(offline_store_configs if offline_store_configs else {}),
            },
            entity_key_serialization_version=3,
        )

    def create_store(self):
        logging.info("Creating feature store with the following configurations:")

        repo_config = self._build_feast_repo_config(
            project_name=self.project_name,
            online_store=self.online_store,
            online_store_configs=self.online_store_configs,
            offline_store=self.offline_store,
            offline_store_configs=self.offline_store_configs,
        )
        repo_path = Path(os.path.join(Path.cwd(), "data"))
        try:
            project, registry, repo, store = _prepare_registry_and_repo(repo_config, repo_path)
            apply_total_with_repo_instance(store, project, registry, repo, True)
            self._fs = FeatureStore(config=repo_config)

            logging.info("Feature store applied successfully.")

            # save the project to the database
            with rx.session() as session:
                session.add(
                    VectorStore(
                        project_name=self.project_name,
                        online_store=self.online_store,
                        offline_store=self.offline_store,
                        online_store_configs=self.online_store_configs,
                        offline_store_configs=self.offline_store_configs,
                    )
                )
                session.commit()
            self.load_store()
        except Exception as e:
            logging.error(f"Error creating feature store: {e}")
            raise e
        finally:

            self.toggle_store_dialog()

    def _create_feature_schema(self):
        return [Field(name=self.feature_name, dtype=Array(Float32))]

    def _create_feature_source(self) -> FeastDataSource:
        if self.feature_datasource == "file":
            return PushSource(
                name=self.feature_view_name,  # feature view name is used to reference the source
                batch_source=FileSource(
                    file_format=ParquetFormat(),
                    path="data/feature.parquet",
                    timestamp_field="event_timestamp",
                ),
            )
        else:
            ds = DataSourceState.get_datasource_by_name(self.feature_datasource)
            if ds.datasource in FEAST_DATASOURCE_MAP:
                return FEAST_DATASOURCE_MAP[ds.datasource](
                    name=self.feature_view_name, **self.feature_source_configs
                )
            else:
                logging.error(f"Data source for {self.feature_datasource} not supported")
            raise ValueError(f"Data source for {self.feature_datasource} not supported")

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

        self._reload_project()

        logging.info("Feature store loaded")

    def load_feature_views(self, feature_view: FeastFeatureView):
        if isinstance(feature_view.source, PushSource):
            self._push_source_to_feature(feature_view)
        else:
            logging.info("Not supported")

    def _push_source_to_feature(self, feature_view: FeastFeatureView):
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
