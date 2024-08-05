from clovers.core.adapter import Adapter
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.qq import (
    Bot,
    AtMessageCreateEvent,
    GUILD_OWNER,
    GUILD_ADMIN,
    GUILD_CHANNEL_ADMIN,
)
from .all import adapter as all_adapter


def adapter(main: type[Matcher]) -> Adapter:

    adapter = Adapter()

    @adapter.kwarg("group_id")
    async def _(event: AtMessageCreateEvent):
        return event.guild_id

    @adapter.kwarg("nickname")
    async def _(event: AtMessageCreateEvent):
        return event.author.username or event.get_user_id()

    @adapter.kwarg("avatar")
    async def _(event: AtMessageCreateEvent):
        return event.author.avatar

    @adapter.kwarg("image_list")
    async def _(event: AtMessageCreateEvent):
        if event.attachments:
            return [url for attachment in event.attachments if (url := attachment.url)]

    @adapter.kwarg("permission")
    async def _(bot: Bot, event: AtMessageCreateEvent) -> int:
        if await SUPERUSER(bot, event):
            return 3
        if await GUILD_OWNER(bot, event):
            return 2
        if await (GUILD_ADMIN | GUILD_CHANNEL_ADMIN)(bot, event):
            return 1
        return 0

    @adapter.kwarg("at")
    async def _(event: AtMessageCreateEvent) -> list[str]:
        if event.mentions:
            return [mention.id for mention in event.mentions]
        return []

    adapter.remix(all_adapter(main))

    return adapter
