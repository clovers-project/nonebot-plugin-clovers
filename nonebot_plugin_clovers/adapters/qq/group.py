from clovers.core.adapter import Adapter
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.adapters.qq import Bot, GroupAtMessageCreateEvent
from .all import adapter as all_adapter


def adapter(main: type[Matcher]) -> Adapter:

    adapter = Adapter()

    @adapter.kwarg("user_id")
    async def _(event: GroupAtMessageCreateEvent):
        return event.author.member_openid

    @adapter.kwarg("group_id")
    async def _(event: GroupAtMessageCreateEvent):
        return event.group_openid

    @adapter.kwarg("image_list")
    async def _(event: GroupAtMessageCreateEvent):
        if event.attachments:
            return [url for attachment in event.attachments if (url := attachment.url)]

    @adapter.kwarg("permission")
    async def _(bot: Bot, event: GroupAtMessageCreateEvent) -> int:
        if await SUPERUSER(bot, event):
            return 3
        return 0

    adapter.remix(all_adapter(main))

    return adapter
