from io import BytesIO
from collections.abc import Callable, AsyncGenerator, Coroutine
from clovers.core.adapter import Adapter
from clovers.core.plugin import Result
from nonebot.matcher import Matcher
from nonebot.adapters.qq import (
    MessageCreateEvent,
    Message,
    MessageSegment,
)


def adapter(main: type[Matcher]) -> Adapter:

    adapter = Adapter()

    @adapter.send("text")
    async def _(message: str, send: Callable[..., Coroutine] = main.send):
        """发送纯文本"""
        await send(message)

    @adapter.send("image")
    async def _(message: bytes | BytesIO | str, send: Callable[..., Coroutine] = main.send):
        """发送图片"""
        if isinstance(message, str):
            await send(MessageSegment.image(message))
        else:
            await send(MessageSegment.file_image(message))

    @adapter.send("voice")
    async def _(message: str, send: Callable[..., Coroutine] = main.send):
        """发送音频消息"""
        await send(MessageSegment.audio(message))

    @adapter.send("list")
    async def _(message: list[Result], send: Callable[..., Coroutine] = main.send):
        """发送图片文本混合信息"""
        msg = Message()
        for seg in message:
            match seg.send_method:
                case "text":
                    msg += seg.data
                case "image":
                    msg += MessageSegment.image(seg.data)
        await send(msg)

    @adapter.send("segmented")
    async def _(message: AsyncGenerator[Result, None], send: Callable[..., Coroutine] = main.send):
        """发送分段信息"""
        async for seg in message:
            await adapter.send_dict[seg.send_method](seg.data, send)

    @adapter.kwarg("user_id")
    async def _(event: MessageCreateEvent):
        return event.get_user_id()

    @adapter.kwarg("to_me")
    async def _(event: MessageCreateEvent):
        return event.to_me

    return adapter
