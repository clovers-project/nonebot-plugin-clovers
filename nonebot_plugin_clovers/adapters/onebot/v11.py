from io import BytesIO
from collections.abc import Callable, Coroutine, AsyncGenerator
from clovers.core.adapter import Adapter
from clovers.core.plugin import Result
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


adapter = Adapter("ONEBOT.V11")
sending: dict[str, Callable[..., Coroutine]] = {}


async def send_text(message: str, send: Callable[..., Coroutine]):
    """发送纯文本"""
    await send(MessageSegment.text(message))


async def send_image(message: bytes | BytesIO | str, send: Callable[..., Coroutine]):
    """发送图片"""
    await send(MessageSegment.image(message))


async def send_voice(message: bytes | BytesIO | str, send: Callable[..., Coroutine]):
    """发送音频消息"""
    await send(MessageSegment.record(message))


async def send_list(message: list[Result], send: Callable[..., Coroutine]):
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


async def send_segmented(message: AsyncGenerator[Result, None], send: Callable[..., Coroutine]):
    """发送分段消息"""
    async for seg in message:
        await sending[seg.send_method](seg.data, send)


sending["text"] = send_text
sending["image"] = send_image
sending["voice"] = send_voice
sending["list"] = send_list
sending["segmented"] = send_segmented


@adapter.send("text")
async def _(message, bot: Bot, event: MessageEvent):
    await send_text(message, lambda message: bot.send(event=event, message=message))


@adapter.send("image")
async def _(message, bot: Bot, event: MessageEvent):
    await send_image(message, lambda message: bot.send(event=event, message=message))


@adapter.send("voice")
async def _(message, bot: Bot, event: MessageEvent):
    await send_voice(message, lambda message: bot.send(event=event, message=message))


@adapter.send("list")
async def _(message, bot: Bot, event: MessageEvent):
    await send_list(message, lambda message: bot.send(event=event, message=message))


@adapter.send("segmented")
async def _(message, bot: Bot, event: MessageEvent):
    await send_segmented(message, lambda message: bot.send(event=event, message=message))


@adapter.kwarg("send_group_message")
async def _(bot: Bot) -> Callable[[str, Result], Coroutine]:
    async def send_group_message(group_id: str, result: Result):
        send = lambda message: bot.send_group_msg(group_id=int(group_id), message=message)
        await sending[result.send_method](result.data, send)

    return send_group_message


@adapter.kwarg("user_id")
async def _(event: MessageEvent):
    return event.get_user_id()


@adapter.kwarg("group_id")
async def _(event: MessageEvent):
    group_id = getattr(event, "group_id", None)
    return str(group_id) if group_id else None


@adapter.kwarg("to_me")
async def _(event: MessageEvent):
    return event.to_me


@adapter.kwarg("nickname")
async def _(event: MessageEvent):
    return event.sender.card or event.sender.nickname


@adapter.kwarg("avatar")
async def _(event: MessageEvent) -> str:
    return f"https://q1.qlogo.cn/g?b=qq&nk={event.user_id}&s=640"


@adapter.kwarg("group_avatar")
async def _(event: MessageEvent) -> str:
    if isinstance(event, GroupMessageEvent):
        return f"https://p.qlogo.cn/gh/{event.group_id}/{event.group_id}/640"
    return ""


@adapter.kwarg("image_list")
async def _(event: MessageEvent):
    url = [msg.data["url"] for msg in event.message if msg.type == "image"]
    if event.reply:
        url += [msg.data["url"] for msg in event.reply.message if msg.type == "image"]
    return url


@adapter.kwarg("permission")
async def _(bot: Bot, event: MessageEvent) -> int:
    if await SUPERUSER(bot, event):
        return 3
    if await GROUP_OWNER(bot, event):
        return 2
    if await GROUP_ADMIN(bot, event):
        return 1
    return 0


@adapter.kwarg("at")
async def _(event: MessageEvent) -> list[str]:
    return [str(msg.data["qq"]) for msg in event.message if msg.type == "at"]


@adapter.kwarg("group_member_list")
async def _(bot: Bot, event: MessageEvent) -> None | list[dict]:
    if not isinstance(event, GroupMessageEvent):
        return None
    info_list = await bot.get_group_member_list(group_id=event.group_id)
    for user_info in info_list:
        user_id = str(user_info["user_id"])
        user_info["user_id"] = user_id
        user_info["avatar"] = f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    return info_list


@adapter.kwarg("group_member_info")
async def _(bot: Bot, event: MessageEvent) -> Callable[[str], Coroutine]:
    async def group_member_info(user_id: str):
        if not isinstance(event, GroupMessageEvent):
            return None
        user_info = await bot.group_member_info(group_id=event.group_id, user_id=int(user_id))
        member_user_id = str(user_info["user_id"])
        user_info["user_id"] = member_user_id
        user_info["avatar"] = f"https://q1.qlogo.cn/g?b=qq&nk={member_user_id}&s=640"

        return user_info

    return group_member_info


__adapter__ = adapter
