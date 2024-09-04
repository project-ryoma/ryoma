import logging
from datetime import datetime
from typing import Any, Optional, Union

import pandas as pd
import reflex as rx
from feast import FeatureStore, RepoConfig
from feast.data_source import DataSource as FeastDataSource
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.embeddings import Embeddings

from ryoma_lab.models.vector_store import (
    FeastFeatureView,
    VectorStore,
    VectorStoreConfig,
)


def retrieve_vector_features(
    fs: FeatureStore,
    feature: str,
    query: list[float],
    top_k: int = 3,
    distance_metric: str = "L2",
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
        "online_store": {
            "type": online_store,
            **online_store_configs,
            "pgvector_enabled": "true",
        },
        "entity_key_serialization_version": 3,
    }

    if offline_store:
        configs["offline_store"] = {
            "type": offline_store,
            **offline_store_configs,
        }
    else:
        configs["offline_config"] = {
            "type": "file",
            "path": "data/registry.db",
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


def get_feature_store(
    store: VectorStore, vector_store_config: VectorStoreConfig
) -> FeatureStore:
    logging.info(f"Getting feature store with store: {store.project_name}")
    repo_config = build_feast_repo_config(
        project_name=store.project_name,
        vector_store_config=vector_store_config,
        online_store=store.online_store,
        online_store_configs=eval(store.online_store_configs)
        if store.online_store_configs
        else "{}",
        offline_store=store.offline_store,
        offline_store_configs=eval(store.offline_store_configs)
        if store.offline_store_configs
        else "{}",
    )
    return FeatureStore(config=repo_config)


def get_feature_views(
    fs: FeatureStore,
) -> list[FeastFeatureView]:
    vector_feature_views = []
    for feature_view in fs.list_feature_views():
        feature_spec = fs.get_feature_view(feature_view.name)
        if feature_spec.stream_source is not None:
            source = feature_spec.stream_source
        else:
            source = feature_spec.batch_source
        vector_feature_views.append(
            FeastFeatureView(
                name=feature_spec.name,
                entities=", ".join(
                    [entity.name for entity in feature_spec.entity_columns]
                ),
                feature=", ".join([feature.name for feature in feature_spec.features]),
                source=source.name,
                source_type=source.__class__.__name__,
                push_source_type=feature_spec.tags.get("push_source_type", ""),
            )
        )
    return vector_feature_views


def load_feature_dataframe(source_dir, file_type):
    if file_type == "parquet":
        return pd.read_parquet(source_dir)
    elif file_type == "csv":
        return pd.read_csv(source_dir)
    elif file_type == "json":
        return pd.read_json(source_dir)
    raise ValueError(f"Unsupported file type: {file_type}")


def validate_feature_dataframe(
    feature_df: pd.DataFrame, feature_view: FeastFeatureView
):
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


def process_file_source(feature_view: FeastFeatureView, file_path: str, file_type: str):
    try:
        df = load_feature_dataframe(file_path, file_type)
        validate_feature_dataframe(df, feature_view)
        return df
    except Exception as e:
        logging.error(f"Error processing file source: {e}")
        raise e


def process_pdf_source(feature_view, source_path) -> dict[str, list[Any]]:
    try:
        docs = PyPDFLoader(source_path).load()
        return {
            "event_timestamp": [datetime.now()] * len(docs),
            feature_view["feature"]: docs,
            feature_view["entities"]: [""] * len(docs),
        }
    except Exception as e:
        logging.error(f"Error processing PDF source: {e}")
        raise e


def apply_embedding(
    embedding_client: Embeddings,
    inputs_data: Union[dict[str, list[Any]], pd.DataFrame],
):
    if not inputs_data:
        return None

    logging.info("Run embedding before indexing feature")
    inputs_data["feature"] = inputs_data["feature"].apply(
        lambda x: embedding_client.embed_query(x) if isinstance(x, str) else x
    )
    return inputs_data


def get_source_path(feature_view: FeastFeatureView):
    root_dir = rx.get_upload_dir()
    source_dir = f"{root_dir}/{feature_view['name']}/{feature_view['source']}"
    return source_dir


def index_feature_from_source(
    fs: FeatureStore,
    feature_view: FeastFeatureView,
    embedding_client: Optional[Embeddings] = None,
):
    logging.info(f"Loading feature view {feature_view}")
    if feature_view["source_type"] == "PushSource":
        push_source_type = feature_view["push_source_type"]
        feature_source_path = get_source_path(feature_view)

        ingest_inputs = None
        if push_source_type in ["parquet", "csv", "json", "txt"]:
            ingest_inputs = process_file_source(
                feature_view, feature_source_path, push_source_type
            )
        elif push_source_type == "pdf":
            ingest_inputs = process_pdf_source(feature_view, feature_source_path)
        else:
            logging.error(f"Unsupported source type: {push_source_type}")
        logging.info(f"Feature view {feature_view} loaded")
        if embedding_client:
            ingest_inputs = apply_embedding(embedding_client, ingest_inputs)
        index_feature(fs, feature_view, ingest_inputs)
    else:
        index_feature_from_offline_source(fs, feature_view)


def index_feature_from_offline_source(fs: FeatureStore, feature_view: FeastFeatureView):
    logging.info(f"Materializing offline feature view {feature_view}")
    fs.materialize_incremental(
        end_date=datetime.now(),
        feature_views=[feature_view["name"]],
    )


def index_feature(
    fs: FeatureStore,
    feature_view: FeastFeatureView,
    inputs: Optional[Union[dict[str, list[Any]], pd.DataFrame]] = None,
):
    logging.info(f"Indexing feature view {feature_view}")
    if isinstance(inputs, pd.DataFrame):
        fs.push(feature_view["source"], inputs)
    else:
        fs.write_to_online_store(
            feature_view_name=feature_view["name"],
            inputs=inputs,
        )
