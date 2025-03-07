from typing import Tuple
from mimetypes import guess_extension
from tempfile import NamedTemporaryFile
from datetime import datetime

from maubot.plugin_base import Plugin
from maubot.matrix import MaubotMessageEvent as MessageEvent
from mautrix.types import MediaInfo, MediaMessageEventContent, MessageType
from mautrix.util.config import BaseProxyConfig
from maubot.handlers import command

from .config import Config
from .utils import extract_file_from_evt
from .transcribe import transcribe_audio


class MauWhisper(Plugin):
    @command.passive("", msgtypes=(MessageType.AUDIO,))
    async def transcribe(self, evt: MessageEvent, _: Tuple[str]) -> None:
        if evt.content.msgtype != MessageType.AUDIO:
            self.log.warning(f"Non-audio msgtype received {evt.content.msgtype}")
            return
        content = evt.content
        if not isinstance(content, MediaMessageEventContent):
            self.log.warning(f"Audio event without media received")
            return

        assert isinstance(self.config, Config)

        if "default_msg" in self.config:
            reply = await evt.reply(self.config["default_msg"])
        else:
            reply = None

        content_info = content.info
        assert isinstance(content_info, MediaInfo)
        mime = content_info.mimetype
        assert isinstance(mime, str)
        mime = mime.split(";", 1)[0]
        suffix = guess_extension(mime)

        with NamedTemporaryFile(suffix=suffix) as f:
            await extract_file_from_evt(content, f, evt.client)

            if self.config.loaded_model is None:
                await evt.respond("No model is loaded.", edits=reply)
                return

            transcribe_params = self.config.transcribe_params()
            self.log.debug(f"Transcribe Params: {transcribe_params}")
            for name, model in self.config.loaded_model:
                self.log.debug(f"Attempting to transcribe using {name}")
                start = datetime.now()

                segments = []
                async for segment in transcribe_audio(
                    f.name, model, self.loop, **transcribe_params
                ):
                    self.log.debug(
                        f"Received segment {segment.text} ({segment.t0} - {segment.t1})"
                    )
                    segments.append(segment.text)
                    if reply is None:
                        reply = await evt.reply(
                            self.config.format_segments(segments),
                            markdown=False,
                            allow_html=False,
                        )
                    else:
                        await evt.respond(
                            self.config.format_segments(segments),
                            markdown=False,
                            allow_html=False,
                            edits=reply,
                        )

                end = datetime.now()
                if self.config["append_model"]:
                    delta = end - start
                    formatted_text = self.config.format_segments(segments)
                    formatted_text += f"\n*(Generated by whisper-{name}. {delta.total_seconds():.2f} seconds used)*"
                    await evt.respond(
                        formatted_text, markdown=True, allow_html=False, edits=reply
                    )

    async def start(self) -> None:
        assert isinstance(self.config, Config)
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> type[BaseProxyConfig]:
        return Config
