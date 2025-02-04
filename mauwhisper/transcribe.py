from typing import Any, AsyncGenerator
from pywhispercpp.model import Model, Segment
import asyncio
import threading


def transcribe_audio(data: str, model: Model) -> AsyncGenerator[Segment, Any]:
    # Adapted from https://stackoverflow.com/a/62297994
    loop = asyncio.get_event_loop()
    q = asyncio.Queue(1)
    exception = None
    _END = object()

    async def yield_queue_items():
        while True:
            next_item = await q.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    def threaded_transcribe():
        nonlocal exception
        try:
            model.transcribe(
                data,
                new_segment_callback=lambda f: asyncio.run_coroutine_threadsafe(
                    q.put(f), loop
                ).result(),
            )
        except Exception as e:
            exception = e
        finally:
            asyncio.run_coroutine_threadsafe(q.put(_END), loop).result()

    threading.Thread(target=threaded_transcribe).start()
    return yield_queue_items()
