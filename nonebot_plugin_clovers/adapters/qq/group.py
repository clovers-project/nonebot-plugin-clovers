from clovers import Adapter
from nonebot.permission import SUPERUSER
from nonebot.adapters.qq import Bot, GroupAtMessageCreateEvent
from .general import adapter as general_adapter


adapter = Adapter("QQ.GROUP")
adapter.remix(general_adapter)


@adapter.property_method("user_id")
async def _(event: GroupAtMessageCreateEvent):
    return event.author.member_openid


@adapter.property_method("group_id")
async def _(event: GroupAtMessageCreateEvent):
    return event.group_openid


@adapter.property_method("image_list")
async def _(event: GroupAtMessageCreateEvent):
    if event.attachments:
        return [url for attachment in event.attachments if (url := attachment.url)]


@adapter.property_method("permission")
async def _(bot: Bot, event: GroupAtMessageCreateEvent) -> int:
    if await SUPERUSER(bot, event):
        return 3
    return 0
