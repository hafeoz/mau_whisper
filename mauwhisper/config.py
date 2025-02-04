from typing import Any, Dict
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
        if "model_dir" in self:
            args["models_dir"] = self["model_dir"]
        if "language" in self:
            args["language"] = self["language"]
        if "prompt" in self:
            args["initial_prompt"] = self["prompt"]
        if "model" not in self:
            return
        self.loaded_model = Model(model=self["model"], **args)

    def params(self) -> Dict[Any, Any]:
        args = {}
        if "language" in self:
            args["language"] = self["language"]
        if "prompt" in self:
            args["initial_prompt"] = self["prompt"]
        return args
