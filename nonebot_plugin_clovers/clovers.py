from functools import wraps
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from clovers import CloversCore
from typing import Protocol, runtime_checkable


@runtime_checkable
class Handler(Protocol):
    async def __call__(self, bot: Bot, event: Event, matcher: Matcher) -> None: ...


class NoneBotCore(CloversCore):
    def __init__(self, adapter_name: str, bot_name: str, plugin_list: list[str], plugin_dirs: list[str], name: str = "NoneBotClovers"):
        super().__init__(name)
        self.BOT_NICKNAME = bot_name
        self.adapter.property_method("bot_nickname")(self.bot_name)
        self.load_adapter([adapter_name])
        self.load_plugin(plugin_list, plugin_dirs)
        self.handler = wraps(self.adapter.calls_lib["none"])(self.handler)

    async def bot_name(self) -> str:
        return self.BOT_NICKNAME

    def extract_message(self, event: Event, **ignore) -> str | None:
        return event.get_plaintext()

    async def handler(self, bot, event, matcher):
        if (coro := self.dispatch(bot=bot, event=event)) and await coro:
            matcher.stop_propagation()
