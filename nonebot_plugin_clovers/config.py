from pydantic import BaseModel
from clovers.config import Config as CloversConfig


class Config(BaseModel):
    plugins: list[str] = []
    plugin_dirs: list[str] = []
    using_adapters: list[str] = [
        "nonebot_plugin_clovers.adapters.onebot.v11",
        "nonebot_plugin_clovers.adapters.qq.group",
        "nonebot_plugin_clovers.adapters.qq.guild",
        "nonebot_plugin_clovers.adapters.satori",
    ]
    nonebot_matcher_priority: int = 100


config_data = CloversConfig.environ().setdefault(__package__, {})
config = Config.model_validate(config_data)
config_data.update(config.model_dump())
