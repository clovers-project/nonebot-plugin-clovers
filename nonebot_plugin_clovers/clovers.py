from pathlib import Path
from functools import wraps, cache
from nonebot import get_driver
from nonebot.matcher import Matcher
from nonebot.adapters import Event
from clovers import Adapter, Leaf, Client as CloversClient
from clovers.utils import list_modules
from clovers.logger import logger
from clovers.config import Config as CloversConfig
from .config import Config
from .adapters.typing import Handler

# 加载 NoneBot 配置
Bot_NICKNAME = next(iter(get_driver().config.nickname), "bot")

__config__: dict = CloversConfig.environ().setdefault(__package__, {})
config = Config.model_validate(__config__)
__config__.update(config.model_dump())


class NoneBotLeaf(Leaf):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter.name)
        self.adapter.update(adapter)
        self.adapter.property_method("Bot_Nickname")(self.Bot_NICKNAME)

    @staticmethod
    async def Bot_NICKNAME() -> str:
        return Bot_NICKNAME

    def extract_message(self, event: Event, **ignore) -> str | None:
        return event.get_plaintext()


class Client(CloversClient):
    def __init__(self, matcher: type[Matcher]):
        super().__init__()
        self.name = "NoneBotCloversClient"
        self.matcher = matcher
        for plugin in config.plugins:
            self.load_plugin(plugin)
        for plugin_dir in config.plugin_dirs:
            plugin_dir = Path(plugin_dir)
            if not plugin_dir.exists():
                plugin_dir.mkdir(parents=True, exist_ok=True)
                continue
            for plugin in list_modules(plugin_dir):
                self.load_plugin(plugin)
        get_driver().on_startup(self.startup)
        get_driver().on_shutdown(self.shutdown)
        self.leafs: list[NoneBotLeaf] = []

    def initialize_plugins(self):
        for leaf in self.leafs:
            leaf.plugins = self.plugins
            leaf.initialize_plugins()
        self._ready = True

    @staticmethod
    def build_handler(handler: Handler, leaf: NoneBotLeaf) -> Handler:
        @wraps(handler)
        async def wrapper(bot, event, matcher):
            if await leaf.response(event=event, bot=bot):
                matcher.stop_propagation()

        return wrapper

    def register_adapter(self, adapter: Adapter, handler: Handler) -> NoneBotLeaf:
        self.leafs.append(leaf := NoneBotLeaf(adapter))
        self.matcher.append_handler(self.build_handler(handler, leaf))
        logger.info(f"{self.name} 注册响应：{leaf.name}")
        return leaf

    async def run(self):
        raise RuntimeError(f"{self.name} 为寄生客户端，不需要独立运行")


@cache
def get_client(matcher: type[Matcher]):
    """获取全局 clovers 客户端"""
    return Client(matcher)
