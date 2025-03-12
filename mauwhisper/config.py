from typing import Any, Dict, List

from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from pywhispercpp.model import Model, Segment


class Config(BaseProxyConfig):
    def reload_model(self) -> None:
        try:
            self.loaded_model.clear()
        except AttributeError:
            self.loaded_model = []

        if "models_dir" in self:
            model_args = {"models_dir": self["models_dir"]}
        else:
            model_args = {}

        self.loaded_model = [
            (model, Model(model=model, **model_args))
            for model in self["models"].split(",")
        ]

    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("default_msg")
        helper.copy("models")
        helper.copy("models_dir")
        helper.copy("language")
        helper.copy("prompt")
        helper.copy("append_model")
        helper.copy("segment_separator")
        helper.copy("segment_formatter")
        self.reload_model()

    def transcribe_params(self) -> Dict[Any, Any]:
        params = {}
        if "language" in self:
            params["language"] = self["language"]
        if "prompt" in self:
            params["initial_prompt"] = self["prompt"]
        return params

    def format_segments(self, segments: List[Segment]) -> str:
        formatted_segments = []
        for segment in segments:
            if "segment_formatter" in self:
                formatted = self["segment_formatter"].format(
                    t0=segment.t0, t1=segment.t1, text=segment.text
                )
            else:
                formatted = segment.text
            formatted_segments.append(formatted)
        if "segment_separator" in self:
            separator = self["separator"]
        else:
            separator = ""
        return separator.join(formatted_segments)
