import os
from pathlib import Path
from nonebot import get_driver, get_plugin_config, on_message
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.log import LoguruHandler, logger
from clovers.core.logger import logger as clovers_logger
from clovers.core.adapter import AdapterMethod
from clovers.core.plugin import PluginLoader
from .adapters.main import extract_command, new_adapter
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
driver.config.log_level
config_data = get_plugin_config(Config)
# 加载配置
clovers_logger.addHandler(LoguruHandler(driver.config.log_level))
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
adapter = new_adapter(loader.plugins)

driver.on_startup(adapter.startup)

main = on_message(priority=clovers_priority, block=False)


def add_response(Bot, Event, adapter_method: AdapterMethod, adapter_key: str):
    logger.info(f"加载适配器：{adapter_key}")
    adapter.method_dict[adapter_key] = adapter_method

    @main.handle()
    async def _(matcher: Matcher, bot: Bot, event: Event):
        command = extract_command(event.get_plaintext())
        if await adapter.response(adapter_key, command, bot=bot, event=event):
            matcher.stop_propagation()


using_adapters = config_data.using_adapters


if "nonebot.adapters.qq" in using_adapters:
    from .adapters import qq
    from nonebot.adapters.qq import Bot, MessageEvent

    add_response(Bot, MessageEvent, qq.initializer(main), "QQ")

if "nonebot.adapters.onebot.v11" in using_adapters:

    from .adapters.onebot import v11
    from nonebot.adapters.onebot.v11 import Bot, MessageEvent

    add_response(Bot, MessageEvent, v11.initializer(main), "onebot.v11".upper())
