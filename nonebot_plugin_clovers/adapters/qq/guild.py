from clovers import Adapter
from nonebot.permission import SUPERUSER
from nonebot.adapters.qq import (
    Bot,
    AtMessageCreateEvent,
    GUILD_OWNER,
    GUILD_ADMIN,
    GUILD_CHANNEL_ADMIN,
)
from .general import adapter as general_adapter

adapter = Adapter("QQ.GUILD")
adapter.remix(general_adapter)


@adapter.property_method("group_id")
async def _(event: AtMessageCreateEvent):
    return event.guild_id


@adapter.property_method("nickname")
async def _(event: AtMessageCreateEvent):
    return event.author.username or event.get_user_id()


@adapter.property_method("avatar")
async def _(event: AtMessageCreateEvent):
    return event.author.avatar


@adapter.property_method("image_list")
async def _(event: AtMessageCreateEvent):
    if event.attachments:
        return [url for attachment in event.attachments if (url := attachment.url)]


@adapter.property_method("permission")
async def _(bot: Bot, event: AtMessageCreateEvent) -> int:
    if await SUPERUSER(bot, event):
        return 3
    if await GUILD_OWNER(bot, event):
        return 2
    if await (GUILD_ADMIN | GUILD_CHANNEL_ADMIN)(bot, event):
        return 1
    return 0


@adapter.property_method("at")
async def _(event: AtMessageCreateEvent) -> list[str]:
    if event.mentions:
        return [mention.id for mention in event.mentions]
    return []
