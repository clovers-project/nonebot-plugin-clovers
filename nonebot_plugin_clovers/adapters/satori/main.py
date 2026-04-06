from clovers import Adapter
from nonebot.permission import SUPERUSER
from nonebot.adapters.satori import Bot, MessageSegment
from nonebot.adapters.satori.event import MessageCreatedEvent
from nonebot.adapters.satori.models import Member
from clovers_client.event import MemberInfo
from clovers_client.result import FileLike, SequenceMessage, SegmentedMessage, GroupMessage, PrivateMessage
from .utils import (
    image2message,
    voice2message,
    video2message,
    file2message,
    list2message,
    send_segmented_result,
    send_result,
)

adapter = Adapter("SATORI")


@adapter.send_method("at")
async def _(message: str, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, MessageSegment.at(message))


@adapter.send_method("text")
async def _(message: str, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, message)


@adapter.send_method("image")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, image2message(message))


@adapter.send_method("list")
async def _(message: SequenceMessage, /, bot: Bot, event: MessageCreatedEvent):
    if msg := list2message(message):
        return await bot.send(event, msg)


@adapter.send_method("voice")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, voice2message(message))


@adapter.send_method("video")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, video2message(message))


@adapter.send_method("file")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, file2message(message))


@adapter.send_method("segmented")
async def _(message: SegmentedMessage, /, bot: Bot, event: MessageCreatedEvent):
    await send_segmented_result(lambda msg: bot.send(event, msg), message)


@adapter.send_method("group_message")
async def _(message: GroupMessage, /, bot: Bot):
    await send_result(lambda msg: bot.send_message(message["group_id"], msg), message["data"])


@adapter.send_method("private_message")
async def _(message: PrivateMessage, /, bot: Bot):
    await send_result(lambda msg: bot.send_private_message(message["user_id"], msg), message["data"])


@adapter.property_method("to_me")
async def _(event: MessageCreatedEvent):
    return event.to_me


@adapter.property_method("at")
async def _(event: MessageCreatedEvent):
    return [seg.data["id"] for seg in event.get_message().query("at")]


@adapter.property_method("image_list")
async def _(event: MessageCreatedEvent):
    url = [seg.data["src"] for seg in event.get_message().query("img")]
    if event.reply:
        url.extend(seg.data["src"] for seg in event.reply.children.query("img"))
    return url


@adapter.property_method("user_id")
async def _(event: MessageCreatedEvent):
    return event.get_user_id()


@adapter.property_method("nickname")
async def _(event: MessageCreatedEvent):
    return event.member.nick or (user.name if (user := event.member.user) else "未知用户") if event.member else "未知用户"


@adapter.property_method("avatar")
async def _(event: MessageCreatedEvent):
    return event.user.avatar or ""


@adapter.property_method("group_id")
async def _(event: MessageCreatedEvent):
    if event.guild:
        return event.guild.id


@adapter.property_method("group_avatar")
async def _(event: MessageCreatedEvent):
    if event.guild:
        return event.guild.avatar


@adapter.property_method("permission")
async def _(bot: Bot, event: MessageCreatedEvent):
    if await SUPERUSER(bot, event):
        return 3
    return 0


# @adapter.property_method("flat_context")
# async def _(bot: Bot, event: MessageCreatedEvent):
#     message = list(event.get_message().query("quote"))
#     if not message:
#         return
#     quote = await bot.message_get(channel_id=event.channel.id, message_id=message[0].data["id"])


def format_member_info(member: Member, group_id: str) -> MemberInfo | None:
    if member.user is None:
        return
    nickname = member.user.name or member.user.nick or member.user.id
    return {
        "user_id": member.user.id,
        "group_id": group_id,
        "avatar": member.user.avatar or "",
        "nickname": nickname,
        "card": member.nick or nickname,
        "last_sent_time": 0,
    }


@adapter.call_method("group_member_list")
async def _(group_id: str, /, bot: Bot) -> list[MemberInfo]:
    member_list = await bot.guild_member_list(guild_id=group_id)
    return [info for member in member_list if (info := format_member_info(member, group_id))]


@adapter.call_method("group_member_info")
async def _(group_id: str, user_id: str, /, bot: Bot) -> MemberInfo:
    member = format_member_info(await bot.guild_member_get(guild_id=group_id, user_id=user_id), group_id)
    if member is None:
        raise ValueError(f"Can't find member:{group_id}-{user_id}")
    return member


__adapter__ = adapter
