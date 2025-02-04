from typing import Any, Dict
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from pywhispercpp.model import Model


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("default_msg")
        helper.copy("models")
        helper.copy("model_dir")
        helper.copy("language")
        helper.copy("prompt")
        helper.copy("append_model")
        helper.copy("segment_separator")

        try:
            self.loaded_model.clear()
        except AttributeError:
            pass
        self.loaded_model = []

        args = {}
        if "model_dir" in self:
            args["models_dir"] = self["model_dir"]
        if "models" not in self:
            return
        self.loaded_model = [
            (model, Model(model=model, **args)) for model in self["models"].split(",")
        ]

    def params(self) -> Dict[Any, Any]:
        args = {}
        if "language" in self:
            args["language"] = self["language"]
        if "prompt" in self:
            args["initial_prompt"] = self["prompt"]
        return args
