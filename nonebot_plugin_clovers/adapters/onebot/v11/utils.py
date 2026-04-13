from collections.abc import Callable, Coroutine
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from clovers_client.result import OverallResult, SegmentedResult
from clovers_client.result import FileLike, SequenceMessage, SegmentedMessage
from nonebot_plugin_clovers.adapters.utils import format_file


def image2message(message: FileLike):
    message = format_file(message)
    return MessageSegment.image(message)


def voice2message(message: FileLike):
    message = format_file(message)
    return MessageSegment.record(message)


def video2message(message: FileLike):
    message = format_file(message)
    return MessageSegment.video(message)


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


def to_message(result: OverallResult):
    match result.key:
        case "at":
            return Message(MessageSegment.at(result.data))
        case "text":
            return Message(MessageSegment.text(result.data))
        case "image":
            return Message(image2message(result.data))
        case "list":
            return Message(list2message(result.data))
        case "voice":
            return Message(voice2message(result.data))
        case "video":
            return Message(video2message(result.data))


async def send_segmented_result(send: Callable[[Message], Coroutine], result: SegmentedMessage):
    async for seg in result:
        if msg := to_message(seg):
            await send(msg)


async def send_result(send: Callable[[Message], Coroutine], result: OverallResult | SegmentedResult):
    if result.key == "segmented":
        await send_segmented_result(send, result.data)
    elif data := to_message(result):
        await send(data)
