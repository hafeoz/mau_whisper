from typing import Tuple
from maubot.plugin_base import Plugin
from maubot.matrix import MaubotMessageEvent as MessageEvent
from mautrix.types import MediaInfo, MediaMessageEventContent, MessageType
from mautrix.util.config import BaseProxyConfig
from maubot.handlers import command
from .config import Config
from .utils import extract_file_from_evt
from .transcribe import transcribe_audio
import mimetypes
import tempfile


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
        reply = await evt.reply(self.config["default_msg"])

        content_info = content.info
        assert isinstance(content_info, MediaInfo)
        mime = content_info.mimetype
        assert isinstance(mime, str)
        mime = mime.split(";", 1)[0]
        file_suffix = mimetypes.guess_extension(mime)

        with tempfile.NamedTemporaryFile(suffix=file_suffix) as f:
            await extract_file_from_evt(content, f, evt.client)

            formatted_text = ""
            async for segment in transcribe_audio(f.name):
                formatted_text += segment.text
                await evt.respond(
                    formatted_text,
                    markdown=False,
                    allow_html=False,
                    edits=reply,
                )

    async def start(self) -> None:
        assert isinstance(self.config, Config)
        self.config.load_and_update()

    @classmethod
    def get_config_class(cls) -> type[BaseProxyConfig]:
        return Config
