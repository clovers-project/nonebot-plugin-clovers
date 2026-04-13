from clovers import Adapter
from clovers.logger import logger
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.qq import Bot, GroupAtMessageCreateEvent, Message, MessageSegment
from clovers_client.event import MemberInfo, PermissionLiteral, FlatContextUnit
from clovers_client.result import FileLike, SequenceMessage, SegmentedMessage, GroupMessage, PrivateMessage
from .utils import (
    image2message,
    voice2message,
    video2message,
    file2message,
    list2message,
    send_segmented_result,
)

ADAPTER = Adapter("QQ.GROUP")


@ADAPTER.call_method("none")
async def handler(bot: Bot, event: GroupAtMessageCreateEvent, matcher: Matcher): ...


@ADAPTER.send_method("at")
async def _(message: str, /, bot: Bot, event: GroupAtMessageCreateEvent):
    await bot.send(message=MessageSegment.mention_user(message), event=event)


@ADAPTER.send_method("text")
async def _(message: str, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return bot.send(message=message, event=event)


@ADAPTER.send_method("image")
def _(message: FileLike, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return bot.send(event=event, message=image2message(message))


@ADAPTER.send_method("list")
def _(message: SequenceMessage, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return bot.send(event=event, message=list2message(message))


@ADAPTER.send_method("voice")
def _(message: FileLike, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return bot.send(event=event, message=voice2message(message))


@ADAPTER.send_method("video")
def _(message: FileLike, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return bot.send(event=event, message=video2message(message))


@ADAPTER.send_method("file")
def _(message: FileLike, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return bot.send(event=event, message=file2message(message))


@ADAPTER.send_method("segmented")
async def _(result: SegmentedMessage, /, bot: Bot, event: GroupAtMessageCreateEvent):
    return await send_segmented_result(lambda msg: bot.send(event, msg), result)


@ADAPTER.property_method("to_me")
async def _(event: GroupAtMessageCreateEvent) -> bool:
    return event.is_tome()


# @ADAPTER.property_method("at")
# async def _(event: GroupAtMessageCreateEvent) -> list[str]:
#     return []


@ADAPTER.property_method("image_list")
async def _(event: GroupAtMessageCreateEvent) -> list[str]:
    if event.attachments:
        return [url for attachment in event.attachments if (attachment.content_type.startswith("image")) and (url := attachment.url)]
    return []


@ADAPTER.property_method("user_id")
async def _(event: GroupAtMessageCreateEvent) -> str:
    return event.get_user_id()


@ADAPTER.property_method("nickname")
async def _(bot: Bot, event: GroupAtMessageCreateEvent) -> str:
    pass
