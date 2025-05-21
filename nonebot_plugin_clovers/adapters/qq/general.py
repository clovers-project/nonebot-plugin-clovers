from clovers import Adapter, Result
from nonebot.adapters.qq import Bot, MessageEvent, Message, MessageSegment
from ..typing import FileLike, ListMessage, SegmentedMessage


def image2message(message: FileLike):
    if isinstance(message, str):
        return MessageSegment.image(message)
    else:
        return MessageSegment.file_image(message)


def voice2message(message: FileLike):
    if isinstance(message, str):
        return MessageSegment.audio(message)
    else:
        return MessageSegment.file_audio(message)


def list2message(message: ListMessage):
    msg = Message()
    for seg in message:
        match seg.key:
            case "text":
                msg += MessageSegment.text(seg.data)
            case "image":
                msg += image2message(seg.data)
    return msg


def to_message(result: Result) -> str | MessageSegment | Message | None:
    match result.key:
        case "text":
            return result.data
        case "image":
            return image2message(result.data)
        case "voice":
            return voice2message(result.data)
        case "list":
            return list2message(result.data)


adapter = Adapter("QQ.General")


@adapter.send_method("text")
async def _(message: str, /, bot: Bot, event: MessageEvent):
    await bot.send(message=message, event=event)


@adapter.send_method("image")
async def _(message: FileLike, /, bot: Bot, event: MessageEvent):
    await bot.send(event=event, message=image2message(message))


@adapter.send_method("voice")
async def _(message: FileLike, /, bot: Bot, event: MessageEvent):
    await bot.send(event=event, message=voice2message(message))


@adapter.send_method("list")
async def _(message: ListMessage, /, bot: Bot, event: MessageEvent):
    await bot.send(event=event, message=list2message(message))


@adapter.send_method("segmented")
async def _(message: SegmentedMessage, /, bot: Bot, event: MessageEvent):
    async for seg in message:
        msg = to_message(seg)
        if msg:
            await bot.send(event=event, message=msg)


@adapter.property_method("user_id")
async def _(event: MessageEvent):
    return event.get_user_id()


@adapter.property_method("to_me")
async def _(event: MessageEvent):
    return event.to_me


__adapter__ = adapter
