from nonebot.matcher import Matcher
from nonebot.adapters.satori import Bot
from nonebot.adapters.satori.event import MessageCreatedEvent
from .main import adapter as ADAPTER


async def handler(bot: Bot, event: MessageCreatedEvent, matcher: Matcher): ...


__all__ = ["ADAPTER", "handler"]
