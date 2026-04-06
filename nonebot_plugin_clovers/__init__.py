from nonebot import on_message, get_driver
from nonebot.plugin import PluginMetadata
from nonebot import get_driver, get_plugin_config
from nonebot.log import LoguruHandler
from clovers.logger import logger as clovers_logger
from .clovers import NoneBotCore
from .config import Config

__all__ = ["NoneBotCore", "__plugin_meta__"]
__plugin_meta__ = PluginMetadata(
    name="NoneBotCloversClient",
    description="对接 NoneBot 框架的 clovers 寄生客户端",
    usage="加载即用",
    type="application",
    homepage="https://github.com/clovers-project/nonebot-plugin-clovers",
    supported_adapters=None,
    config=Config,
)
# 配置日志记录器
LOG_LEVEL = get_driver().config.log_level
clovers_logger.setLevel(LOG_LEVEL)
clovers_logger.addHandler(LoguruHandler(LOG_LEVEL))
# 加载插件配置
plugin_config = get_plugin_config(Config).clovers
plugins = plugin_config.plugins
plugin_dirs = plugin_config.plugin_dirs
using_adapters = plugin_config.using_adapters
priority = plugin_config.matcher_priority
# 创建 NoneBotCloversClient
driver = get_driver()
bot_name = next(iter(driver.config.nickname), "bot")
matcher = on_message(priority=priority, block=False)
for adapter in using_adapters:
    package = adapter.replace("~", f"{__package__}.adapters.")
    core = NoneBotCore(package, bot_name, plugins, plugin_dirs)
    driver.on_startup(core.startup)
    driver.on_shutdown(core.shutdown)
    matcher.append_handler(core.handler)
    clovers_logger.info(f"NoneBotCloversClient 注册响应：{core.adapter.name}")
