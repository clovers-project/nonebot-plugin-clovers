from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from .main import adapter as ADAPTER


async def handler(bot: Bot, event: Event, matcher: Matcher): ...


__all__ = ["ADAPTER", "handler"]
