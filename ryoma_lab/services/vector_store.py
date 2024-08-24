from typing import Optional

import json
import logging

from feast import FeatureStore, RepoConfig
from feast.data_source import DataSource as FeastDataSource

from ryoma_lab.models.vector_store import FeastFeatureView, VectorStore, VectorStoreConfig


def retrieve_vector_features(
    fs: FeatureStore, feature: str, query: list[float], top_k: int = 3, distance_metric: str = "L2"
) -> dict:
    logging.info(f"Retrieving online documents for {feature} with vector")
    response = fs.retrieve_online_documents(
        feature=feature, query=query, top_k=top_k, distance_metric=distance_metric
    )
    logging.info(f"Retrieved online documents: {response.to_dict()}")
    return response.to_dict()


def build_feast_repo_config(
    project_name,
    vector_store_config: VectorStoreConfig,
    online_store: str,
    online_store_configs: dict[str, str],
    offline_store: Optional[str] = None,
    offline_store_configs: Optional[dict[str, str]] = None,
):
    logging.info(f"Building feast repo config with project name: {project_name}")
    configs = {
        "project": project_name,
        "provider": "local",
        "registry": {
            "type": vector_store_config.registry_type,
            "path": vector_store_config.path,
        },
        "entity_key_serialization_version": 3,
    }
    if online_store:
        configs["online_store"] = {
            "type": online_store,
            **online_store_configs,
            "pgvector_enabled": "true",
        }
    if offline_store:
        configs["offline_store"] = {
            "type": offline_store,
            **offline_store_configs,
        }
    return RepoConfig(**configs)


def get_feast_datasource_by_name(ds: str) -> Optional[FeastDataSource]:
    from feast import BigQuerySource, RedshiftSource, SnowflakeSource
    from feast.infra.offline_stores.contrib.postgres_offline_store.postgres_source import (
        PostgreSQLSource,
    )

    feast_datasource_map = {
        "postgresql": PostgreSQLSource,
        "snowflake": SnowflakeSource,
        "bigquery": BigQuerySource,
        "redshift": RedshiftSource,
    }
    if ds not in feast_datasource_map:
        return None
    return feast_datasource_map[ds]


def get_feature_store(store: VectorStore, vector_store_config: VectorStoreConfig) -> FeatureStore:
    logging.info(f"Getting feature store with store: {store.project_name}")
    repo_config = build_feast_repo_config(
        project_name=store.project_name,
        vector_store_config=vector_store_config,
        online_store=store.online_store,
        online_store_configs=json.loads(
            store.online_store_configs if store.online_store_configs else "{}"
        ),
        offline_store=store.offline_store,
        offline_store_configs=json.loads(
            store.offline_store_configs if store.offline_store_configs else "{}"
        ),
    )
    return FeatureStore(config=repo_config)


def get_feature_views(
    fs: FeatureStore,
) -> list[FeastFeatureView]:
    vector_feature_views = []
    for feature_view in fs.list_feature_views():
        feature_spec = fs.get_feature_view(feature_view.name)
        vector_feature_views.append(
            FeastFeatureView(
                name=feature_spec.name,
                entities=", ".join([entity.name for entity in feature_spec.entity_columns]),
                feature=", ".join([feature.name for feature in feature_spec.features]),
                source=feature_spec.stream_source.name,
                source_type=feature_spec.stream_source.__class__.__name__,
                push_source_type=feature_spec.tags.get("push_source_type", ""),
            )
        )
    return vector_feature_views
