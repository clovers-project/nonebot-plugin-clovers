from clovers import Leaf, Adapter, Result
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    GroupMessageEvent,
    Message,
    MessageSegment,
    GROUP_ADMIN,
    GROUP_OWNER,
)
from ..typing import FileLike, ListMessage, SegmentedMessage, GroupMessage, PrivateMessage


async def handler(bot: Bot, event: MessageEvent, matcher: Matcher): ...


adapter = Adapter("ONEBOT.V11")


def list2message(message: ListMessage):
    msg = Message()
    for seg in message:
        match seg.send_method:
            case "text":
                msg += MessageSegment.text(seg.data)
            case "image":
                msg += MessageSegment.image(seg.data)
            case "at":
                msg += MessageSegment.at(seg.data) + " "
    return msg


def to_message(result: Result) -> str | Message | None:
    match result.send_method:
        case "text":
            return result.data
        case "image":
            return Message(MessageSegment.image(result.data))
        case "voice":
            return Message(MessageSegment.record(result.data))
        case "list":
            return list2message(result.data)


@adapter.send_method("text")
async def _(message: str, /, bot: Bot, event: MessageEvent):
    await bot.send(message=message, event=event)


@adapter.send_method("image")
async def _(message: FileLike, /, bot: Bot, event: MessageEvent):
    await bot.send(message=MessageSegment.image(message), event=event)


@adapter.send_method("voice")
async def _(message: FileLike, /, bot: Bot, event: MessageEvent):
    await bot.send(message=MessageSegment.record(message), event=event)


@adapter.send_method("list")
async def _(message: ListMessage, /, bot: Bot, event: MessageEvent):
    await bot.send(message=list2message(message), event=event)


@adapter.send_method("segmented")
async def _(message: SegmentedMessage, /, bot: Bot, event: MessageEvent):
    async for seg in message:
        msg = to_message(seg)
        if msg:
            await bot.send(message=msg, event=event)


@adapter.send_method("merge_forward")
async def _(message: ListMessage, /, bot: Bot, event: MessageEvent):
    messages = [
        {"type": "node", "data": {"name": event.self_id, "uin": event.self_id, "content": content}}
        for seg in message
        if (content := to_message(seg))
    ]
    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(group_id=event.group_id, messages=messages)
    else:
        await bot.send_private_forward_msg(user_id=event.user_id, messages=messages)


@adapter.send_method("group_message")
async def _(message: GroupMessage, /, bot: Bot):
    result = message["data"]
    group_id = int(message["group_id"])
    if result.send_method == "segmented":
        async for seg in result.data:
            msg = to_message(seg)
            if msg:
                await bot.send_group_msg(group_id=group_id, message=msg)
    else:
        msg = to_message(result)
        if msg:
            await bot.send_group_msg(group_id=group_id, message=msg)


@adapter.send_method("private_message")
async def _(message: PrivateMessage, /, bot: Bot):
    result = message["data"]
    user_id = int(message["user_id"])
    if result.send_method == "segmented":
        async for seg in result.data:
            msg = to_message(seg)
            if msg:
                await bot.send_private_msg(user_id=user_id, message=msg)
    else:
        msg = to_message(result)
        if msg:
            await bot.send_private_msg(user_id=user_id, message=msg)


@adapter.property_method("user_id")
async def _(event: MessageEvent):
    return event.get_user_id()


@adapter.property_method("group_id")
async def _(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return str(event.group_id)


@adapter.property_method("to_me")
async def _(event: MessageEvent):
    return event.to_me


@adapter.property_method("nickname")
async def _(event: MessageEvent):
    return event.sender.card or event.sender.nickname


@adapter.property_method("avatar")
async def _(event: MessageEvent):
    return f"https://q1.qlogo.cn/g?b=qq&nk={event.user_id}&s=640"


@adapter.property_method("group_avatar")
async def _(event: MessageEvent):
    if isinstance(event, GroupMessageEvent):
        return f"https://p.qlogo.cn/gh/{event.group_id}/{event.group_id}/640"


@adapter.property_method("image_list")
async def _(event: MessageEvent):
    url = [msg.data["url"] for msg in event.message if msg.type == "image"]
    if event.reply:
        url += [msg.data["url"] for msg in event.reply.message if msg.type == "image"]
    return url


@adapter.property_method("permission")
async def _(bot: Bot, event: MessageEvent) -> int:
    if await SUPERUSER(bot, event):
        return 3
    if await GROUP_OWNER(bot, event):
        return 2
    if await GROUP_ADMIN(bot, event):
        return 1
    return 0


@adapter.property_method("at")
async def _(event: MessageEvent) -> list[str]:
    return [str(msg.data["qq"]) for msg in event.message if msg.type == "at"]


@adapter.call_method("group_member_list")
async def _(group_id: str, /, bot: Bot):
    info_list = await bot.get_group_member_list(group_id=int(group_id))
    for user_info in info_list:
        user_id = str(user_info["user_id"])
        user_info["group_id"] = str(user_info["group_id"])
        user_info["user_id"] = user_id
        user_info["avatar"] = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    return info_list


@adapter.call_method("group_member_info")
async def _(group_id: str, user_id: str, /, bot: Bot):
    user_info = await bot.get_group_member_info(group_id=int(group_id), user_id=int(user_id))
    member_user_id = str(user_info["user_id"])
    user_info["group_id"] = str(user_info["group_id"])
    user_info["user_id"] = member_user_id
    user_info["avatar"] = f"https://q1.qlogo.cn/g?b=qq&nk={member_user_id}&s=640"
    return user_info


__adapter__ = adapter
