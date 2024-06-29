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


class VectorStore(rx.Model, table=True):
    project_name: str
    online_store_type: str
    offline_store_type: Optional[str]
    online_store_configs: Optional[str]
    offline_store_configs: Optional[str]


class FeastFeature(rx.Model):
    name: str
    schema: str
    entities: Optional[str] = ""
    source: Optional[str] = ""
    ttl: Optional[int] = None


class VectorStoreState(BaseState):
    projects: list[VectorStore] = []
    project_names: list[str] = []

    project_name: str
    online_store_type: str
    offline_store_type: Optional[str] = ""
    online_store_configs: str
    offline_store_configs: Optional[str] = ""

    feature_name: str
    feature_schema: str
    feature_entities: Optional[str] = None
    feature_source: Optional[str] = ""
    feature_ttl: Optional[int] = None

    vector_features: list[FeastFeature] = []

    store_dialog_open: bool = False
    feature_dialog_open: bool = False

    _fs: Optional[FeatureStore] = None

    def open_feature_dialog(self):
        self.feature_dialog_open = not self.feature_dialog_open

    def open_store_dialog(self):
        self.store_dialog_open = not self.store_dialog_open

    def set_project(self, project_name: str):
        self.project_name = project_name
        print(f"Project name: {self.project_name}")
        self._load_project()

    def _load_project(self):
        project = next(
            (project for project in self.projects if project.project_name == self.project_name),
            None,
        )
        if project:
            repo_config = self._get_feast_repo_config(
                project_name=project.project_name,
                online_store_type=project.online_store_type,
                online_store_configs=project.online_store_configs,
                offline_store_type=project.offline_store_type,
                offline_store_configs=project.offline_store_configs,
            )
            self._fs = FeatureStore(config=repo_config)
            self.vector_features = self._get_features()

    def _get_feast_repo_config(
        self,
        project_name,
        online_store_type,
        online_store_configs,
        offline_store_type: Optional[str] = None,
        offline_store_configs: Optional[str] = None,
    ):
        return RepoConfig(
            project=project_name,
            registry="data/vector.db",
            provider="local",
            online_config={
                **json.loads(online_store_configs),
                "type": online_store_type,
            },
            offline_config={
                **(json.loads(offline_store_configs) if offline_store_configs else {}),
                "type": offline_store_type,
            },
            entity_key_serialization_version=3,
        )

    def create_store(self):
        repo_config = self._get_feast_repo_config(
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
            logging.info("Feature store created")
        except Exception as e:
            logging.error(f"Error creating feature store: {e}")
            raise e
        finally:
            self.open_store_dialog()

    def _create_feature_schema(self):
        return [Field(name=self.feature_schema, dtype=Array(Float32))]

    def _create_feature_source(self):
        return PushSource(
            name=self.feature_source,
            batch_source=FileSource(
                file_format=ParquetFormat(),
                path="data/feature.parquet",
                timestamp_field="event_timestamp",
            ),
        )

    def create_vector_feature(self):
        self._fs.apply(
            FeatureView(
                name=self.feature_name,
                entities=self.feature_entities,
                schema=self._create_feature_schema(),
                source=self._create_feature_source(),
                ttl=self.feature_ttl,
            )
        )
        logging.info(f"Feature {self.feature_name} created")
        self.open_feature_dialog()

    def _embed(self, text: str):
        pass

    def _get_features(self) -> list[FeastFeature]:
        vector_features = []
        for feature_view in self._fs.list_feature_views():
            feature_spec = self._fs.get_feature_view(feature_view.name)
            vector_features.append(
                FeastFeature(
                    name=feature_spec.name,
                    entities=", ".join(feature_spec.entities),
                    schema=", ".join(
                        [f"{schema.name}:{schema.dtype}" for schema in feature_spec.schema]
                    ),
                    source=feature_spec.batch_source.name,
                    ttl=feature_spec.ttl.seconds if feature_spec.ttl else None,
                )
            )
        return vector_features

    def load_store(self):
        with rx.session() as session:
            self.projects = session.exec(select(VectorStore)).all()
            self.project_names = [project.project_name for project in self.projects]

        # load the features from the first project
        if self.projects and len(self.projects) > 0:
            self.project_name = self.projects[0].project_name
            repo_config = self._get_feast_repo_config(
                project_name=self.project_name,
                online_store_type=self.projects[0].online_store_type,
                online_store_configs=self.projects[0].online_store_configs,
                offline_store_type=self.projects[0].offline_store_type,
                offline_store_configs=self.projects[0].offline_store_configs,
            )
            self._fs = FeatureStore(config=repo_config)
            self.vector_features = self._get_features()

        logging.info("Feature store loaded")

    def load_vector_feature(self):
        feature_data_frame = pd.DataFrame(
            {
                "test_schema": [[1.0, 2.0, 3.0]],
                "event_timestamp": pd.to_datetime(["2021-01-01"]),
                "__dummy_id": ["1"],
            }
        )
        try:
            self._fs.push(self.feature_source, feature_data_frame)
            logging.info(f"Feature {self.feature_name} loaded")
        except Exception as e:
            logging.error(f"Error loading feature: {e}")
            raise e

    def _retrieve_vector_features(self, feature: str, query, top_k: int = 3) -> dict:
        logging.info(f"Retrieving online documents for {feature} with query {query}")
        response = self._fs.retrieve_online_documents(feature=feature, query=query, top_k=top_k)
        return response.to_dict()

    def on_load(self) -> None:
        self.load_store()
