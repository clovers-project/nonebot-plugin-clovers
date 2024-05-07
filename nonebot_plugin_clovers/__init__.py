import os
from pathlib import Path
from nonebot import get_driver, get_plugin_config, on_message
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.log import LoguruHandler, logger
from nonebot.adapters import (
    Bot as BaseBot,
    Event as BaseEvent,
)
from collections.abc import Callable
from clovers.core.logger import logger as clovers_logger
from clovers.core.adapter import Adapter
from clovers.core.plugin import PluginLoader
from .adapters.main import extract_command, new_clovers
from .config import Config, ConfigClovers

__plugin_meta__ = PluginMetadata(
    name="clovers插件框架",
    description="NoneBot clovers框架",
    usage="加载即用",
    type="application",
    homepage="https://github.com/KarisAya/nonebot_plugin_clovers",
    config=Config,
)
driver = get_driver()
# 配置日志记录器
log_level = driver.config.log_level
clovers_logger.setLevel(log_level)
clovers_logger.addHandler(LoguruHandler(log_level))
# 加载配置
config_data = get_plugin_config(Config)
clovers_config_file = config_data.clovers_config_file
clovers_priority = config_data.clovers_priority

os.environ["clovers_config_file"] = clovers_config_file

# 添加环境变量之后加载config

from clovers.core.config import config as clovers_config

config_key = __package__
clovers_config_data = ConfigClovers.model_validate(clovers_config.get(config_key, {}))
clovers_config[config_key] = clovers_config_data.model_dump()
clovers_config.save()

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


using_adapters = __plugin_meta__.supported_adapters = config_data.using_adapters

main = on_message(priority=clovers_priority, block=False)

if "nonebot.adapters.onebot.v11" in using_adapters:
    try:
        from nonebot.adapters.onebot.v11 import Bot, MessageEvent
        from .adapters.onebot import v11

        logger.success("nonebot.adapters.onebot.v11 加载成功！")
        flag = True
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.onebot.v11 加载失败...")
        flag = False

    if flag:
        add_response(main, Bot, MessageEvent, v11.adapter(main), "onebot.v11".upper())

if "nonebot.adapters.qq" in using_adapters:
    try:
        from nonebot.adapters.qq import Bot, MessageCreateEvent
        from .adapters import qq

        logger.success("nonebot.adapters.qq 加载成功！")
        flag = True
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.qq 加载失败...")
        flag = False

    if flag:
        add_response(main, Bot, MessageCreateEvent, qq.adapter(main), "QQ")

if "nonebot.adapters.satori" in using_adapters:
    try:
        from nonebot.adapters.satori import Bot
        from nonebot.adapters.satori.event import MessageCreatedEvent
        from .adapters import satori

        logger.success("nonebot.adapters.satori 加载成功！")
        flag = True
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.satori 加载失败...")
        flag = False

    if flag:
        add_response(main, Bot, MessageCreatedEvent, satori.adapter(main), "satori".upper())
