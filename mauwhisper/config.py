from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from pywhispercpp.model import Model


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("default_msg")
        helper.copy("model")
        helper.copy("model_dir")
        helper.copy("language")
        helper.copy("prompt")
        try:
            del self.loaded_model
        except AttributeError:
            pass
        self.loaded_model = Model(
            model=self["model"],
            models_dir=self["model_dir"],
            language=self["language"],
            initial_prompt=self["prompt"],
        )
