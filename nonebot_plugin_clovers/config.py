from pydantic import BaseModel


class NBPluginConfig(BaseModel):
    clovers_using_adapters: list[str] = [
        "nonebot_plugin_clovers.adapters.onebot.v11",
        "nonebot_plugin_clovers.adapters.qq.group",
        "nonebot_plugin_clovers.adapters.qq.guild",
        "nonebot_plugin_clovers.adapters.satori",
    ]
    clovers_matcher_priority: int = 100


class Config(BaseModel):
    plugins: list[str] = []
    plugin_dirs: list[str] = []
