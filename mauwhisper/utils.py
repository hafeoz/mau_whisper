from typing import IO

from mautrix.crypto.attachments import decrypt_attachment
from mautrix.types import MediaMessageEventContent
from mautrix.client import Client


async def extract_file_from_evt(
    content: MediaMessageEventContent, out_file: IO[bytes], client: Client
) -> None:
    if content.url:
        data = await client.download_media(content.url)
    elif content.file:
        url = content.file.url
        if url is None:
            raise ValueError
        data = decrypt_attachment(
            await client.download_media(url),
            content.file.key.key,
            content.file.hashes["sha256"],
            content.file.iv,
        )
    else:
        raise ValueError
    out_file.write(data)
    out_file.flush()
