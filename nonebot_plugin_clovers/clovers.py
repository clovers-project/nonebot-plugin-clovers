from functools import wraps
from nonebot.adapters import Event
from clovers import CloversCore


class NoneBotCore(CloversCore):
    def __init__(self, adapter_name: str, bot_name: str, plugin_list: list[str], plugin_dirs: list[str], name: str = "NoneBotClovers"):
        super().__init__(name)
        self.BOT_NICKNAME = bot_name
        self.adapter.property_method("bot_nickname")(self.bot_name)
        self.load_adapter([adapter_name])
        self.load_plugin(plugin_list, plugin_dirs)

        async def handler(bot, event, matcher):
            if (coro := self.dispatch(bot=bot, event=event)) and await coro:
                matcher.stop_propagation()

        self.handler = wraps(self.adapter.calls_lib["none"])(handler)

    async def bot_name(self) -> str:
        return self.BOT_NICKNAME

    def extract_message(self, event: Event, **ignore) -> str | None:
        return event.get_plaintext()
