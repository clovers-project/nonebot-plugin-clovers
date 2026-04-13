from collections.abc import Callable, Coroutine
from nonebot.adapters.qq import Message, MessageSegment
from clovers_client.result import FileLike, SequenceMessage, SegmentedMessage, Result
from nonebot_plugin_clovers.adapters.utils import format_file


def image2message(message: FileLike):
    message = format_file(message)
    if isinstance(message, str):
        return MessageSegment.image(message)
    else:
        return MessageSegment.file_image(message)


def voice2message(message: FileLike):
    message = format_file(message)
    if isinstance(message, str):
        return MessageSegment.audio(message)
    else:
        return MessageSegment.file_audio(message)


def video2message(message: FileLike):
    message = format_file(message)
    if isinstance(message, str):
        return MessageSegment.video(message)
    else:
        return MessageSegment.file_video(message)


def file2message(message: FileLike):
    message = format_file(message)
    if isinstance(message, str):
        return MessageSegment.file(message)
    else:
        return MessageSegment.file_file(message)


def list2message(message: SequenceMessage):
    msg = Message()
    for seg in message:
        match seg.key:
            case "text":
                msg += MessageSegment.text(seg.data)
            case "image":
                msg += image2message(seg.data)
            case "at":
                msg += MessageSegment.mention_user(seg.data)
    return msg


def to_message(result: Result):
    match result.key:
        case "at":
            return MessageSegment.mention_user(result.data)
        case "text":
            return MessageSegment.text(result.data)
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


async def send_segmented_result(send: Callable[[Message | MessageSegment], Coroutine], result: SegmentedMessage):
    async for seg in result:
        if msg := to_message(seg):
            await send(msg)
