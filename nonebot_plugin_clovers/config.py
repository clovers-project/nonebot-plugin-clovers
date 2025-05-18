from pydantic import BaseModel


class Config(BaseModel):
    plugins: list[str] = []
    plugin_dirs: list[str] = []
    using_adapters: list[str] = [
        "nonebot_plugin_clovers.adapters.onebot.v11",
        "nonebot_plugin_clovers.adapters.qq.group",
        "nonebot_plugin_clovers.adapters.qq.guild",
        "nonebot_plugin_clovers.adapters.satori",
    ]


from clovers.config import config as clovers_config

__config__ = Config.model_validate(clovers_config.get("clovers", {}))
clovers_config["clovers"] = __config__.model_dump()
