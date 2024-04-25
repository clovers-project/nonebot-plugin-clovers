from pydantic import BaseModel


class Config(BaseModel):
    clovers_config_file: str = "clovers.toml"
    clovers_priority: int = 50
    using_adapters: set[str] = {}


class ConfigClovers(BaseModel):
    plugins_path: str = "./clovers_library"
    plugins_list: list = []
