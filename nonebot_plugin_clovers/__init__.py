from pathlib import Path
from nonebot import get_driver, get_plugin_config, on_message
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.log import LoguruHandler, logger
from nonebot.adapters import (
    Bot as BaseBot,
    Event as BaseEvent,
)
from clovers.core.logger import logger as clovers_logger
from clovers.core.adapter import Adapter
from clovers.core.plugin import PluginLoader
from clovers.core.config import config as clovers_config
from .adapters.main import extract_command, new_clovers
from .config import Config, ConfigClovers

__plugin_meta__ = PluginMetadata(
    name="clovers插件框架",
    description="NoneBot clovers框架",
    usage="加载即用",
    type="application",
    homepage="https://github.com/KarisAya/nonebot_plugin_clovers",
    supported_adapters={
        "nonebot.adapters.qq",
        "nonebot.adapters.onebot.v11",
        "nonebot.adapters.satori",
    },
    config=Config,
)
driver = get_driver()
# 配置日志记录器
log_level = driver.config.log_level
clovers_logger.setLevel(log_level)
clovers_logger.addHandler(LoguruHandler(log_level))

# 加载基础配置
config_key = "clovers"
clovers_config_data = ConfigClovers.model_validate(clovers_config.get(config_key, {}))
clovers_config[config_key] = clovers_config_data.model_dump()
clovers_config.save()

# 初始化
plugins_path = Path(clovers_config_data.plugins_path)
plugins_path.mkdir(exist_ok=True, parents=True)
clovers = new_clovers(PluginLoader(plugins_path, clovers_config_data.plugins_list).plugins)
driver.on_startup(clovers.startup)


def add_response(
    main: type[Matcher],
    Bot: type[BaseBot],
    Event: type[BaseEvent],
    adapter: Adapter,
    adapter_key: str,
):
    clovers.adapter_dict[adapter_key] = adapter

    @main.handle()
    async def _(matcher: Matcher, bot: Bot, event: Event):
        command = extract_command(event.get_plaintext())
        if await clovers.response(adapter_key, command, bot=bot, event=event):
            matcher.stop_propagation()


# 加载配置
config_data = get_plugin_config(Config)
clovers_priority = config_data.clovers_priority
using_adapters = config_data.using_adapters

main = on_message(priority=clovers_priority, block=False)

if "nonebot.adapters.onebot.v11" in using_adapters:
    try:
        from nonebot.adapters.onebot.v11 import Bot, MessageEvent
        from .adapters.onebot.v11 import adapter as v11_adapter

        add_response(main, Bot, MessageEvent, v11_adapter(main), "onebot.v11".upper())
        logger.success("nonebot.adapters.onebot.v11 加载成功！")
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.onebot.v11 加载失败...")


if "nonebot.adapters.qq" in using_adapters:
    try:
        from nonebot.adapters.qq import Bot, AtMessageCreateEvent, GroupAtMessageCreateEvent
        from .adapters.qq.guild import adapter as qq_guild_adapter
        from .adapters.qq.group import adapter as qq_group_adapter

        add_response(main, Bot, GroupAtMessageCreateEvent, qq_group_adapter(main), "QQ-GROUP")
        add_response(main, Bot, AtMessageCreateEvent, qq_guild_adapter(main), "QQ-GUILD")
        logger.success("nonebot.adapters.qq 加载成功！")
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.qq 加载失败...")


if "nonebot.adapters.satori" in using_adapters:
    try:
        from nonebot.adapters.satori import Bot
        from nonebot.adapters.satori.event import MessageCreatedEvent
        from .adapters.satori import adapter as satori_adapter

        add_response(main, Bot, MessageCreatedEvent, satori_adapter(main), "satori".upper())
        logger.success("nonebot.adapters.satori 加载成功！")
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.satori 加载失败...")
