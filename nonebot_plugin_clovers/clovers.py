from functools import wraps
from importlib import import_module
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from clovers import CloversCore


class NoneBotCore(CloversCore):
    def __init__(
        self,
        adapter_name: str,
        bot_name: str,
        plugin_list: list[str],
        plugin_dirs: list[str],
    ):
        super().__init__("NoneBotClovers")

        @wraps(import_module(adapter_name).handler)
        async def handler(bot, event, matcher):
            if (coro := self.dispatch(bot=bot, event=event)) and await coro:
                matcher.stop_propagation()

        self.handler = handler
        self.adapter.property_method("Bot_Nickname")(self.bot_name)
        adapter = self.adapter.load(adapter_name)
        assert adapter
        self.adapter.name = f"{self.adapter.name}.{adapter.name}"
        self.plugins.load_plugin(plugin_list, plugin_dirs)
        self.BOT_NICKNAME = bot_name

    @staticmethod
    async def handler(bot: Bot, event: Event, matcher: Matcher) -> None: ...

    async def bot_name(self) -> str:
        return self.BOT_NICKNAME

    def extract_message(self, event: Event, **ignore) -> str | None:
        return event.get_plaintext()
