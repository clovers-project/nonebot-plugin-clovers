from pydantic import BaseModel


class Config(BaseModel):
    clovers_config_file: str = "clovers.toml"
    clovers_priority: int = 50
    using_adapters: set[str] = {
        "nonebot.adapters.qq",
        "nonebot.adapters.onebot.v11",
        "nonebot.adapters.satori",
    }


class ConfigClovers(BaseModel):
    plugins_path: str = "./clovers_library"
    plugins_list: list = []
