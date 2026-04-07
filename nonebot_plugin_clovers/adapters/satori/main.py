from clovers import Adapter
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.adapters.satori import Bot, MessageSegment
from nonebot.adapters.satori.event import MessageCreatedEvent
from nonebot.adapters.satori.models import Member
from clovers_client.event import MemberInfo, PermissionLiteral
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

ADAPTER = Adapter("SATORI")


@ADAPTER.call_method("none")
async def handler(bot: Bot, event: MessageCreatedEvent, matcher: Matcher): ...


@ADAPTER.send_method("at")
async def _(message: str, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, MessageSegment.at(message))


@ADAPTER.send_method("text")
async def _(message: str, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, message)


@ADAPTER.send_method("image")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, image2message(message))


@ADAPTER.send_method("list")
async def _(message: SequenceMessage, /, bot: Bot, event: MessageCreatedEvent):
    if msg := list2message(message):
        return await bot.send(event, msg)


@ADAPTER.send_method("voice")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, voice2message(message))


@ADAPTER.send_method("video")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, video2message(message))


@ADAPTER.send_method("file")
async def _(message: FileLike, /, bot: Bot, event: MessageCreatedEvent):
    await bot.send(event, file2message(message))


@ADAPTER.send_method("segmented")
async def _(message: SegmentedMessage, /, bot: Bot, event: MessageCreatedEvent):
    await send_segmented_result(lambda msg: bot.send(event, msg), message)


@ADAPTER.send_method("group_message")
async def _(message: GroupMessage, /, bot: Bot):
    await send_result(lambda msg: bot.send_message(message["group_id"], msg), message["data"])


@ADAPTER.send_method("private_message")
async def _(message: PrivateMessage, /, bot: Bot):
    await send_result(lambda msg: bot.send_private_message(message["user_id"], msg), message["data"])


@ADAPTER.property_method("to_me")
async def _(event: MessageCreatedEvent) -> bool:
    return event.to_me


@ADAPTER.property_method("at")
async def _(event: MessageCreatedEvent) -> list[str]:
    return [seg.data["id"] for seg in event.get_message().query("at")]


@ADAPTER.property_method("image_list")
async def _(event: MessageCreatedEvent) -> list[str]:
    url = [seg.data["src"] for seg in event.get_message().query("img")]
    if event.reply:
        url.extend(seg.data["src"] for seg in event.reply.children.query("img"))
    return url


@ADAPTER.property_method("user_id")
async def _(event: MessageCreatedEvent) -> str:
    return event.get_user_id()


@ADAPTER.property_method("nickname")
async def _(event: MessageCreatedEvent) -> str:
    if member := event.member:
        if user := member.user:
            return user.nick or user.name or "未知用户"
        return member.nick or "未知用户"
    return "未知用户"


@ADAPTER.property_method("avatar")
async def _(event: MessageCreatedEvent) -> str:
    return event.user.avatar or ""


@ADAPTER.property_method("group_id")
async def _(event: MessageCreatedEvent) -> str | None:
    if event.guild:
        return event.guild.id


@ADAPTER.property_method("group_avatar")
async def _(event: MessageCreatedEvent) -> str | None:
    if event.guild:
        return event.guild.avatar


@ADAPTER.property_method("permission")
async def _(bot: Bot, event: MessageCreatedEvent) -> PermissionLiteral:
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


@ADAPTER.call_method("group_member_list")
async def _(group_id: str, /, bot: Bot) -> list[MemberInfo]:
    member_list = await bot.guild_member_list(guild_id=group_id)
    return [info for member in member_list if (info := format_member_info(member, group_id))]


@ADAPTER.call_method("group_member_info")
async def _(group_id: str, user_id: str, /, bot: Bot) -> MemberInfo:
    member = format_member_info(await bot.guild_member_get(guild_id=group_id, user_id=user_id), group_id)
    if member is None:
        raise ValueError(f"Can't find member:{group_id}-{user_id}")
    return member
