import os
from pathlib import Path
from nonebot import get_driver, get_plugin_config, on_message
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.log import LoguruHandler, logger
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
    supported_adapters={
        "nonebot.adapters.qq",
        "nonebot.adapters.onebot.v11",
    },
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

loader = PluginLoader(plugins_path, clovers_config_data.plugins_list)

clovers = new_clovers(loader.plugins)

driver.on_startup(clovers.startup)

main = on_message(priority=clovers_priority, block=False)


def add_response(Bot, Event, adapter: Adapter, adapter_key: str):
    logger.info(f"加载适配器：{adapter_key}")
    clovers.adapter_dict[adapter_key] = adapter

    @main.handle()
    async def _(matcher: Matcher, bot: Bot, event: Event):
        command = extract_command(event.get_plaintext())
        if await clovers.response(adapter_key, command, bot=bot, event=event):
            matcher.stop_propagation()


using_adapters = config_data.using_adapters


flag_name = lambda flag: "成功！" if flag else "失败..."

if "nonebot.adapters.qq" in using_adapters:
    flag = True
    try:
        from .adapters import qq
        from nonebot.adapters.qq import Bot, MessageEvent
    except ModuleNotFoundError:
        logger.error("nonebot.adapters.qq 加载失败...")
        flag = False
    if flag:
        add_response(Bot, MessageEvent, qq.initializer(main), "QQ")
        logger.success("nonebot.adapters.qq 加载成功！")

if "nonebot.adapters.onebot.v11" in using_adapters:
    flag = True
    try:
        from .adapters.onebot import v11
        from nonebot.adapters.onebot.v11 import Bot, MessageEvent
    except ModuleNotFoundError:
        flag = False
        logger.error("nonebot.adapters.onebot.v11 加载失败...")
    if flag:
        add_response(Bot, MessageEvent, v11.initializer(main), "onebot.v11".upper())
        logger.success("nonebot.adapters.onebot.v11 加载成功！")
