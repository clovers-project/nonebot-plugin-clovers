from io import BytesIO
from collections.abc import Callable, AsyncGenerator, Coroutine
from clovers.core.adapter import Adapter
from clovers.core.plugin import Result
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.qq import (
    Bot,
    MessageEvent,
    AtMessageCreateEvent,
    GroupAtMessageCreateEvent,
    Message,
    MessageSegment,
    GUILD_OWNER,
    GUILD_ADMIN,
    GUILD_CHANNEL_ADMIN,
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

    @adapter.kwarg("send_group_message")
    async def _(bot: Bot, event: MessageEvent) -> Callable[[int, Result], Coroutine]:
        async def send_group_message(group_id: int, result: Result):
            send = lambda message: bot.send_group_msg(group_id=group_id, message=message)
            await adapter.send_dict[result.send_method](result.data, send)

        return send_group_message

    @adapter.kwarg("user_id")
    async def _(event: MessageEvent):
        return event.get_user_id()

    @adapter.kwarg("group_id")
    async def _(event: MessageEvent):
        return getattr(event, "group_id", getattr(event, "guild_id", None))

    @adapter.kwarg("to_me")
    async def _(event: MessageEvent):
        return event.to_me

    @adapter.kwarg("nickname")
    async def _(event: MessageEvent):
        if isinstance(event, AtMessageCreateEvent):
            return event.author.username or event.get_user_id()
        return event.get_user_id()

    @adapter.kwarg("avatar")
    async def _(event: MessageEvent):
        if isinstance(event, AtMessageCreateEvent):
            return event.author.avatar
        return None

    # @adapter.kwarg("group_avatar")
    # async def _(event: MessageEvent) -> str:
    #     pass

    @adapter.kwarg("image_list")
    async def _(event: MessageEvent):
        if isinstance(event, AtMessageCreateEvent | GroupAtMessageCreateEvent):
            if event.attachments:
                return [url for attachment in event.attachments if (url := attachment.url)]
            return []

    @adapter.kwarg("permission")
    async def _(bot: Bot, event: MessageEvent) -> int:
        if await SUPERUSER(bot, event):
            return 3
        if isinstance(event, AtMessageCreateEvent):
            if await GUILD_OWNER(bot, event):
                return 2
            if await (GUILD_ADMIN | GUILD_CHANNEL_ADMIN)(bot, event):
                return 1
            return 0
        else:
            return 0

    @adapter.kwarg("at")
    async def _(event: MessageEvent) -> list[str]:
        if isinstance(event, AtMessageCreateEvent) and event.mentions:
            print(event.mentions)
            return [mention.id for mention in event.mentions]
        return []

    # @adapter.kwarg("group_member_list")
    # async def _(bot: Bot, event: MessageEvent) -> None | list[dict]:
    #     pass

    return adapter
