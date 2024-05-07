from io import BytesIO
from collections.abc import Callable, Coroutine, AsyncGenerator
from clovers.core.adapter import Adapter
from clovers.core.plugin import Result
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.satori import (
    Bot,
    Message,
    MessageSegment,
)
from nonebot.adapters.satori.event import MessageCreatedEvent


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
            await send(MessageSegment.image(url=message))
        else:
            await send(MessageSegment.image(raw=message, mime="image"))

    @adapter.send("voice")
    async def _(message: bytes | BytesIO | str, send: Callable[..., Coroutine] = main.send):
        """发送音频消息"""
        if isinstance(message, str):
            await send(MessageSegment.audio(url=message))
        else:
            await send(MessageSegment.audio(raw=message, mime="audio"))

    @adapter.send("list")
    async def _(message: list[Result], send: Callable[..., Coroutine] = main.send):
        """发送图片文本混合信息，@信息在此发送"""
        msg = Message()
        for seg in message:
            match seg.send_method:
                case "text":
                    msg += MessageSegment.text(seg.data)
                case "image":
                    msg += MessageSegment.image(seg.data)
                case "at":
                    msg += MessageSegment.at(seg.data)
        await send(msg)

    @adapter.send("segmented")
    async def _(message: AsyncGenerator[Result, None], send: Callable[..., Coroutine] = main.send):
        """发送分段信息"""
        async for seg in message:
            await adapter.send_dict[seg.send_method](seg.data, send)

    @adapter.kwarg("send_group_message")
    async def _(bot: Bot) -> Callable[[str, Result], Coroutine]:
        async def send_group_message(group_id: str, result: Result):
            send = lambda message: bot.send_message(channel_id=group_id, message=message)
            await adapter.send_dict[result.send_method](result.data, send)

        return send_group_message

    @adapter.kwarg("user_id")
    async def _(event: MessageCreatedEvent):
        return event.get_user_id()

    @adapter.kwarg("group_id")
    async def _(event: MessageCreatedEvent):
        if event.guild:
            return event.guild.id

    @adapter.kwarg("to_me")
    async def _(event: MessageCreatedEvent):
        return event.to_me

    @adapter.kwarg("nickname")
    async def _(event: MessageCreatedEvent):
        if event.member:
            return event.member.nick or event.member.name

    @adapter.kwarg("avatar")
    async def _(event: MessageCreatedEvent):
        return event.user.avatar

    @adapter.kwarg("group_avatar")
    async def _(event: MessageCreatedEvent):
        if event.guild:
            return event.guild.avatar

    @adapter.kwarg("image_list")
    async def _(event: MessageCreatedEvent):
        url = [msg.data["src"] for msg in event._message if msg.type == "img"]
        if event.reply:
            url += [msg.data["src"] for msg in event.reply._children if msg.type == "img"]
        return url

    @adapter.kwarg("permission")
    async def _(bot: Bot, event: MessageCreatedEvent) -> int:
        if await SUPERUSER(bot, event):
            return 3
        return 0

    @adapter.kwarg("at")
    async def _(event: MessageCreatedEvent) -> list[str]:
        return [str(msg.data["id"]) for msg in event._message if msg.type == "at"]

    return adapter
