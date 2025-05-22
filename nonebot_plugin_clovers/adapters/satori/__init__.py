from pathlib import Path
from clovers import Adapter, Result
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.adapters.satori import Bot, Message, MessageSegment
from nonebot.adapters.satori.event import MessageCreatedEvent
from ..typing import (
    FileLike,
    ListMessage,
    SegmentedMessage,
    GroupMessage,
    PrivateMessage,
)


async def handler(bot: Bot, event: MessageCreatedEvent, matcher: Matcher): ...


def image2message(message: FileLike):
    if isinstance(message, str):
        return MessageSegment.image(url=message)
    else:
        raw = message.read_bytes() if isinstance(message, Path) else message
        return MessageSegment.image(raw=raw, mime="image")


def voice2message(message: FileLike):
    if isinstance(message, str):
        return MessageSegment.audio(url=message)
    else:
        raw = message.read_bytes() if isinstance(message, Path) else message
        return MessageSegment.audio(raw=raw, mime="audio")


def list2message(message: ListMessage):
    msg = Message()
    for seg in message:
        match seg.key:
            case "text":
                msg += MessageSegment.text(seg.data)
            case "image":
                msg += image2message(seg.data)
            case "at":
                msg += MessageSegment.at(seg.data)
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


adapter = Adapter("SATORI")


@adapter.send_method("text")
async def _(message: str, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event=event, message=message)


@adapter.send_method("image")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event=event, message=image2message(message))


@adapter.send_method("voice")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event=event, message=voice2message(message))


@adapter.send_method("list")
async def _(message: ListMessage, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event=event, message=list2message(message))


@adapter.send_method("segmented")
async def _(message: SegmentedMessage, /, bot: Bot, event: MessageCreatedEvent):
    async for seg in message:
        msg = to_message(seg)
        if msg:
            await bot.send(event=event, message=msg)


@adapter.send_method("group_message")
async def _(message: GroupMessage, /, bot: Bot):
    result = message["data"]
    group_id = message["group_id"]
    if result.key == "segmented":
        async for seg in result.data:
            msg = to_message(seg)
            if msg:
                await bot.send_message(channel=group_id, message=msg)
    else:
        msg = to_message(result)
        if msg:
            await bot.send_message(channel=group_id, message=msg)


@adapter.send_method("private_message")
async def _(message: PrivateMessage, /, bot: Bot):
    result = message["data"]
    user_id = message["user_id"]
    if result.key == "segmented":
        async for seg in result.data:
            msg = to_message(seg)
            if msg:
                await bot.send_private_message(user=user_id, message=msg)
    else:
        msg = to_message(result)
        if msg:
            await bot.send_private_message(user=user_id, message=msg)


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
        return event.member.nick or (user.name if (user := event.member.user) else None)


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
        user_info["nickname"] = member.nick
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
    user_info["nickname"] = member.nick
    user_info["card"] = member.nick
    return user_info


__adapter__ = adapter
