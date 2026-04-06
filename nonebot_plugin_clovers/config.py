from pydantic import BaseModel


class ScopedConfig(BaseModel):
    using_adapters: list[str] = ["~onebot.v11", "~qq.group", "~qq.guild", "~satori", "~uninfo"]
    matcher_priority: int = 100
    plugins: list[str] = []
    plugin_dirs: list[str] = []


class Config(ScopedConfig):
    clovers: ScopedConfig
