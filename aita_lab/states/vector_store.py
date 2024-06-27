from typing import Optional

import reflex as rx
from feast.feature_store import FeatureStore
from feast.repo_config import RepoConfig

from aita_lab.states.base import BaseState


class VectorStore(rx.Model):
    project_name: str
    project_configs: Optional[dict]

    online_store_type: str
    offline_store_type: Optional[str]
    online_store_configs: Optional[dict]
    offline_store_configs: Optional[dict]
    project_configs: Optional[dict]


class VectorStoreState(BaseState):
    project_name: str
    project_configs: Optional[dict]

    online_store_type: str
    offline_store_type: Optional[str] = ""
    online_store_configs: Optional[dict]
    offline_store_configs: Optional[dict]

    store_dialog_open: bool = False
    feature_dialog_open: bool = False

    _fs: Optional[FeatureStore] = None

    def open_feature_dialog(self):
        self.feature_dialog_open = not self.feature_dialog_open

    def open_store_dialog(self):
        self.store_dialog_open = not self.store_dialog_open

    def create_store(self):
        self._fs = FeatureStore(
            config=RepoConfig(
                project=self.project_name,
                registry="/reflex.db",
                provider="local",
                online_store={
                    "type": self.online_store_type,
                    **self.online_store_configs,
                },
                offline_store={
                    "type": self.offline_store_type,
                    **self.offline_store_configs,
                },
            )
        )

    def create_feature(self, feature):
        pass

    def _embed(self, text: str):
        pass
