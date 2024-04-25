from io import BytesIO
from collections.abc import Callable, AsyncGenerator
from clovers.core.adapter import Adapter
from clovers.core.plugin import Result
from nonebot.matcher import Matcher
from nonebot.adapters.qq import MessageEvent, Message, MessageSegment


def initializer(main: type[Matcher]) -> Adapter:

    adapter = Adapter()

    @adapter.send("text")
    async def _(message: str):
        """发送纯文本"""
        await main.send(message)

    @adapter.send("image_url")
    async def _(message: str, main: type[Matcher]):
        """发送图片"""
        await main.send(MessageSegment.image(message))

    @adapter.send("image")
    async def _(message: BytesIO, main: type[Matcher]):
        """发送图片"""
        await main.send(MessageSegment.file_image(message))

    @adapter.send("list")
    async def _(message: list[Result], main: type[Matcher]):
        """发送图片文本混合信息"""
        msg = Message()
        for seg in message:
            if seg.send_method == "text":
                msg += seg.data
            elif seg.send_method == "image":
                msg += MessageSegment.image(seg.data)
        await main.send(msg)

    @adapter.send("segmented")
    async def _(message: AsyncGenerator[Result, None]):
        """发送分段信息"""
        async for seg in message:
            await adapter.send_dict[seg.send_method](seg.data)

    @adapter.kwarg("user_id")
    async def _(event: MessageEvent):
        return event.get_user_id()

    @adapter.kwarg("group_id")
    async def _(event: MessageEvent):
        return getattr(event, "group_id", getattr(event, "guild_id", None))

    return adapter
