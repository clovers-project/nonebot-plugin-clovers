from io import BytesIO
from pathlib import Path
from collections.abc import Callable, AsyncGenerator, Coroutine
from clovers.adapter import Adapter
from clovers.plugin import Result
from nonebot.adapters.qq import (
    Bot,
    MessageEvent,
    Message,
    MessageSegment,
)

adapter = Adapter("QQ.General")
sending: dict[str, Callable[..., Coroutine]] = {}


async def send_text(message: str, send: Callable[..., Coroutine]):
    """发送纯文本"""
    await send(MessageSegment.text(message))


async def send_image(message: bytes | BytesIO | str | Path, send: Callable[..., Coroutine]):
    """发送图片"""
    if isinstance(message, str):
        await send(MessageSegment.image(message))
    else:
        await send(MessageSegment.file_image(message))


async def send_voice(message: bytes | BytesIO | str | Path, send: Callable[..., Coroutine]):
    """发送音频消息"""
    if isinstance(message, str):
        await send(MessageSegment.audio(message))
    else:
        await send(MessageSegment.file_audio(message))


async def send_list(message: list[Result], send: Callable[..., Coroutine]):
    """发送图片文本混合信息"""
    msg = Message()
    for seg in message:
        match seg.send_method:
            case "text":
                msg += seg.data
            case "image":
                if isinstance(message, str):
                    await send(MessageSegment.image(seg.data))
                else:
                    await send(MessageSegment.file_image(seg.data))
    await send(msg)


async def send_segmented(message: AsyncGenerator[Result, None], send: Callable[..., Coroutine]):
    """发送分段消息"""
    async for seg in message:
        await sending[seg.send_method](seg.data, send)


sending["text"] = send_text
sending["image"] = send_image
sending["voice"] = send_voice
sending["list"] = send_list
sending["segmented"] = send_segmented


@adapter.send_method("text")
async def _(message, /, bot: Bot, event: MessageEvent):
    await send_text(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("image")
async def _(message, /, bot: Bot, event: MessageEvent):
    await send_image(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("voice")
async def _(message, /, bot: Bot, event: MessageEvent):
    await send_voice(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("list")
async def _(message, /, bot: Bot, event: MessageEvent):
    await send_list(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("segmented")
async def _(message, /, bot: Bot, event: MessageEvent):
    await send_segmented(message, lambda message: bot.send(event=event, message=message))


@adapter.property_method("user_id")
async def _(event: MessageEvent):
    return event.get_user_id()


@adapter.property_method("to_me")
async def _(event: MessageEvent):
    return event.to_me
