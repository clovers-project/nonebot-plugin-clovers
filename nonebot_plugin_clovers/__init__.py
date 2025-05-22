from importlib import import_module
from nonebot.plugin import PluginMetadata
from nonebot import get_driver, get_plugin_config
from nonebot.log import logger, LoguruHandler
from clovers.logger import logger as clovers_logger
from clovers import Adapter
from .adapters.typing import Handler
from .clovers import get_client
from .config import NBPluginConfig

__plugin_meta__ = PluginMetadata(
    name="NoneBotCloversClient",
    description="对接 NoneBot 框架的 clovers 寄生客户端",
    usage="加载即用",
    type="application",
    homepage="https://github.com/clovers-project/nonebot-plugin-clovers",
    supported_adapters=None,
    config=NBPluginConfig,
)
# 配置日志记录器
log_level = get_driver().config.log_level
clovers_logger.setLevel(log_level)
clovers_logger.addHandler(LoguruHandler(log_level))

# 加载插件配置
nb_config = get_plugin_config(NBPluginConfig)
using_adapters = nb_config.clovers_using_adapters
priority = nb_config.clovers_matcher_priority

# 创建 NoneBotCloversClient

client = get_client(priority)

for import_name in using_adapters:
    try:
        module = import_module(import_name)
        adapter = getattr(module, "__adapter__", None)
        assert adapter and isinstance(adapter, Adapter), f"{import_name} adapter is not valid"
        handler = getattr(module, "handler", None)
        assert handler and isinstance(handler, Handler), f"{import_name} handler is not valid"
        client.register_adapter(adapter, handler)
    except Exception:
        logger.exception(f"{import_name} 加载失败")
