from typing import Any, AsyncGenerator
from asyncio import AbstractEventLoop, Queue, run_coroutine_threadsafe
from threading import Thread

from pywhispercpp.model import Model, Segment


def transcribe_audio(
    data: str, model: Model, loop: AbstractEventLoop, **params
) -> AsyncGenerator[Segment, Any]:
    # Adapted from https://stackoverflow.com/a/62297994
    q = Queue(1)
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
                new_segment_callback=lambda f: run_coroutine_threadsafe(
                    q.put(f), loop
                ).result(),
                **params
            )
        except Exception as e:
            exception = e
        finally:
            run_coroutine_threadsafe(q.put(_END), loop).result()

    Thread(target=threaded_transcribe).start()
    return yield_queue_items()
