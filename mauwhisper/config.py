from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from pywhispercpp.model import Model
from .transcribe import loaded_model


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("default_msg")
        helper.copy("model")
        helper.copy("model_dir")
        helper.copy("language")
        global loaded_model
        loaded_model = Model(
            model=self["model"], models_dir=self["model_dir"], language=self["language"]
        )
