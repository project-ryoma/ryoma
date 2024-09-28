from typing import Optional

import reflex as rx


class VectorStoreConfig(rx.Base):
    """
    VectorStoreConfig is a model that holds the configuration for storying the registry data.
    It will be used by feast to apply the feature store.
    """

    registry_type: str
    path: str


class FeatureViewModel(rx.Model):
    name: str
    feature: str
    entities: Optional[str] = ""
    source: str = ""
    source_type: str = ""
    push_source_type: str = ""


class VectorStore(rx.Model, table=True):
    project_name: str
    online_store: str
    online_store_configs: Optional[str]
    offline_store: str
    offline_store_configs: Optional[str]
