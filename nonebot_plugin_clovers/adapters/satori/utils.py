from pathlib import Path
from collections.abc import Callable, Coroutine
from nonebot.adapters.satori import Message, MessageSegment
from clovers_client.result import FileLike, SequenceMessage, SegmentedMessage, Result
from nonebot_plugin_clovers.adapters.utils import format_file, format_filename


def image2message(message: FileLike):
    message = format_file(message)
    match message:
        case str():
            return MessageSegment.image(url=message)
        case Path():
            return MessageSegment.image(path=message)
        case _:
            return MessageSegment.image(raw=message, mime="image")


def voice2message(message: FileLike):
    message = format_file(message)
    match message:
        case str():
            return MessageSegment.audio(url=message)
        case Path():
            return MessageSegment.audio(path=message)
        case _:
            return MessageSegment.audio(raw=message, mime="audio")


def video2message(message: FileLike):
    message = format_file(message)
    match message:
        case str():
            return MessageSegment.video(url=message)
        case Path():
            return MessageSegment.video(path=message)
        case _:
            return MessageSegment.video(raw=message, mime="video")


def file2message(message: FileLike):
    filename = format_filename(message)
    message = format_file(message)
    match message:
        case str():
            return MessageSegment.file(url=message, name=filename)
        case Path():
            return MessageSegment.file(path=message, name=filename)
        case _:
            return MessageSegment.file(raw=message, mime="text", name=filename)


def list2message(message: SequenceMessage):
    msg = Message()
    for seg in message:
        match seg.key:
            case "text":
                msg += MessageSegment.text(seg.data)
            case "image":
                msg += image2message(seg.data)
            case "at":
                msg += MessageSegment.at(seg.data)
                msg += MessageSegment.text(" ")
    return msg


def to_message(result: Result):
    match result.key:
        case "at":
            return MessageSegment.at(result.data)
        case "text":
            return result.data
        case "image":
            return image2message(result.data)
        case "list":
            return list2message(result.data)
        case "voice":
            return voice2message(result.data)
        case "video":
            return video2message(result.data)
        case "file":
            return file2message(result.data)


type Sendable = str | Message | MessageSegment


async def send_segmented_result(send: Callable[[Sendable], Coroutine], result: SegmentedMessage):
    async for seg in result:
        if msg := to_message(seg):
            await send(msg)


async def send_result(send: Callable[[Sendable], Coroutine], result: Result):
    if result.key == "segmented":
        await send_segmented_result(send, result.data)
    elif data := to_message(result):
        await send(data)
