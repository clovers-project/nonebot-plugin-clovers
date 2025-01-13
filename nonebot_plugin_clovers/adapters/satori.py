from io import BytesIO
from collections.abc import Callable, Coroutine, AsyncGenerator
from clovers import Adapter, Result
from nonebot.permission import SUPERUSER
from nonebot.adapters.satori import Bot, Message, MessageSegment
from nonebot.adapters.satori.event import MessageCreatedEvent

adapter = Adapter("SATORI")
sending: dict[str, Callable[..., Coroutine]] = {}


async def send_text(message: str, send: Callable[..., Coroutine]):
    """发送纯文本"""
    await send(MessageSegment.text(message))


async def send_image(message: bytes | BytesIO | str, send: Callable[..., Coroutine]):
    """发送图片"""
    if isinstance(message, str):
        await send(MessageSegment.image(url=message))
    else:
        await send(MessageSegment.image(raw=message, mime="image"))


async def send_voice(message: bytes | BytesIO | str, send: Callable[..., Coroutine]):
    """发送音频消息"""
    if isinstance(message, str):
        await send(MessageSegment.audio(url=message))
    else:
        await send(MessageSegment.audio(raw=message, mime="audio"))


async def send_list(message: list[Result], send: Callable[..., Coroutine]):
    """发送图片文本混合信息，@信息在此发送"""
    msg = Message()
    for seg in message:
        match seg.send_method:
            case "text":
                msg += MessageSegment.text(seg.data)
            case "image":
                if isinstance(message, str):
                    await send(MessageSegment.image(url=seg.data))
                else:
                    await send(MessageSegment.image(raw=seg.data, mime="image"))
            case "at":
                msg += MessageSegment.at(seg.data)
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
async def _(message, /, bot: Bot, event: MessageCreatedEvent):
    await send_text(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("image")
async def _(message, /, bot: Bot, event: MessageCreatedEvent):
    await send_image(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("voice")
async def _(message, /, bot: Bot, event: MessageCreatedEvent):
    await send_voice(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("list")
async def _(message, /, bot: Bot, event: MessageCreatedEvent):
    await send_list(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("segmented")
async def _(message, /, bot: Bot, event: MessageCreatedEvent):
    await send_segmented(message, lambda message: bot.send(event=event, message=message))


@adapter.send_method("group_message")
async def _(message: dict, /, bot: Bot):
    # Result("group_message", {"group_id": "123", "data": Result("text", "xxx")})
    result: Result = message["data"]
    group_id = message["group_id"]
    await sending[result.send_method](result.data, lambda message: bot.send_message(channel_id=group_id, message=message))


@adapter.send_method("private_message")
async def _(message: dict, /, bot: Bot):
    # Result("group_message", {"user_id": "123", "data": Result("text", "xxx")})
    result: Result = message["data"]
    user_id = message["user_id"]
    await sending[result.send_method](result.data, lambda message: bot.send_private_message(user_id=user_id, message=message))


# properties = ["user_id", "group_id", "to_me", "nickname", "avatar", "group_avatar", "image_list", "permission", "at"]


@adapter.property_method("user_id")
async def _(event: MessageCreatedEvent):
    return event.get_user_id()


@adapter.property_method("group_id")
async def _(event: MessageCreatedEvent):
    if event.guild:
        return event.guild.id


@adapter.property_method("to_me")
async def _(event: MessageCreatedEvent):
    return event.to_me


@adapter.property_method("nickname")
async def _(event: MessageCreatedEvent):
    if event.member:
        return event.member.nick or event.member.name


@adapter.property_method("avatar")
async def _(event: MessageCreatedEvent):
    return event.user.avatar


@adapter.property_method("group_avatar")
async def _(event: MessageCreatedEvent):
    if event.guild:
        return event.guild.avatar


@adapter.property_method("image_list")
async def _(event: MessageCreatedEvent):
    url = [msg.data["src"] for msg in event._message if msg.type == "img"]
    if event.reply:
        url += [msg.data["src"] for msg in event.reply._children if msg.type == "img"]
    return url


@adapter.property_method("permission")
async def _(bot: Bot, event: MessageCreatedEvent):
    if await SUPERUSER(bot, event):
        return 3
    return 0


@adapter.property_method("at")
async def _(event: MessageCreatedEvent):
    return [str(msg.data["id"]) for msg in event._message if msg.type == "at"]


@adapter.call_method("group_member_list")
async def _(group_id: str, /, bot: Bot):
    member_list = await bot.guild_member_list(guild_id=group_id)
    info_list = []
    for member in member_list.data:
        if not member.user:
            continue
        user_info = member.model_dump()
        user_info["user_id"] = member.user.id
        user_info["group_id"] = group_id
        user_info["avatar"] = member.avatar
        user_info["nickname"] = member.name
        user_info["card"] = member.nick
        info_list.append(user_info)
    return info_list


@adapter.call_method("group_member_info")
async def _(group_id: str, user_id: str, /, bot: Bot):
    member = await bot.guild_member_get(guild_id=group_id, user_id=user_id)
    if not member.user:
        return None
    user_info = member.model_dump()
    user_info["user_id"] = member.user.id
    user_info["group_id"] = group_id
    user_info["avatar"] = member.avatar
    user_info["nickname"] = member.name
    user_info["card"] = member.nick
    return user_info
