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

        args = {}
        if self["model_dir"] is str:
            args["models_dir"] = self["model_dir"]
        if self["language"] is str:
            args["language"] = self["language"]
        if self["initial_prompt"] is str:
            args["initial_prompt"] = self["initial_prompt"]
        self.loaded_model = Model(model=self["model"], **args)
