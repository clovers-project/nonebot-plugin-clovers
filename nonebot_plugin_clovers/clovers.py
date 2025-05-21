from pathlib import Path
from functools import wraps
from nonebot import on_message, get_driver
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot.log import LoguruHandler
from clovers import Leaf, Client as CloversClient, Adapter
from clovers.utils import list_modules
from clovers.logger import logger
from .config import __config__
from .adapters.typing import Handler


__plugin_meta__ = PluginMetadata(
    name="clovers插件框架",
    description="NoneBot clovers框架",
    usage="加载即用",
    type="library",
    homepage="https://github.com/KarisAya/nonebot_plugin_clovers",
    supported_adapters=None,
    config=None,
)
# 配置日志记录器
log_level = get_driver().config.log_level
logger.setLevel(log_level)
logger.addHandler(LoguruHandler(log_level))

# 加载 NoneBot 配置
nonebot_config = get_driver().config
command_start = [x for x in nonebot_config.command_start if x]
Bot_NICKNAME = next(iter(nonebot_config.nickname), "bot")
priority = __config__.nonebot_matcher_priority


async def get_Bot_NICKNAME() -> str:
    return Bot_NICKNAME


class NoneBotLeaf(Leaf):
    def __init__(self, adapter: Adapter):
        super().__init__(adapter.name)
        self.adapter.update(adapter)
        self.adapter.property_method("Bot_Nickname")(get_Bot_NICKNAME)

    if command_start:

        def extract_message(self, event: Event, **ignore) -> str | None:
            message = event.get_plaintext()
            for x in command_start:
                if message.startswith(x):
                    return message.lstrip(x)
            return message

    else:

        def extract_message(self, event: Event, **ignore) -> str | None:
            return event.get_plaintext()


class Client(CloversClient):
    def __init__(self, priority=100):
        super().__init__()
        self.name = "NoneBotCloversClient"
        self.matcher = on_message(priority=priority, block=False)
        for plugin in __config__.plugins:
            self.load_plugin(plugin)
        for plugin_dir in __config__.plugin_dirs:
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


_client: Client | None = None


def get_client():
    """获取全局 clovers 客户端"""
    global _client
    if _client is None:
        _client = Client()
    return _client
