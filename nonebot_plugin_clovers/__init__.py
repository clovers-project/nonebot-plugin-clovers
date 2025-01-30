from pathlib import Path
from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from nonebot.log import LoguruHandler
from pathlib import Path
from clovers import Clovers
from clovers.tools import list_modules
from clovers.logger import logger as clovers_logger
from clovers.config import config as clovers_config

__plugin_meta__ = PluginMetadata(
    name="clovers插件框架",
    description="NoneBot clovers框架",
    usage="加载即用",
    type="library",
    homepage="https://github.com/KarisAya/nonebot_plugin_clovers",
    supported_adapters=None,
    config=None,
)
driver = get_driver()
clovers = Clovers()
# 配置日志记录器
log_level = driver.config.log_level
clovers_logger.setLevel(log_level)
clovers_logger.addHandler(LoguruHandler(log_level))

# 加载 Clovers配置
config_key = "clovers"
clovers_config[config_key] = clovers_config.get(config_key, {})

# 加载 NoneBot 配置
nonebot_config = driver.config
command_start = [x for x in nonebot_config.command_start if x]
Bot_NICKNAME = Bot_NICKNAMEs[0] if (Bot_NICKNAMEs := list(nonebot_config.nickname)) else "bot"

clovers_config[config_key]["Bot_NICKNAME"] = Bot_NICKNAME

plugins: list[str] = clovers_config[config_key].setdefault("plugins", [])
adapters: list[str] = clovers_config[config_key].setdefault("adapters", [])
plugin_dirs: list[str] = clovers_config[config_key].setdefault("plugin_dirs", [])
adapters_dirs: list[str] = clovers_config[config_key].setdefault("adapters_dirs", [])

if command_start:

    def extract_command(message: str) -> str:
        for x in command_start:
            if message.startswith(x):
                return message.lstrip(x)
        return message

else:

    def extract_command(message: str) -> str:
        return message


@clovers.adapter.property_method("Bot_Nickname")
async def _():
    return Bot_NICKNAME


# 初始化
clovers.load_adapters(adapters)
for dir in adapters_dirs:
    Path(dir).mkdir(exist_ok=True, parents=True)
    clovers.load_adapters(list_modules(dir))


clovers.load_plugins(plugins)
for dir in plugin_dirs:
    Path(dir).mkdir(exist_ok=True, parents=True)
    clovers.load_plugins(list_modules(dir))
