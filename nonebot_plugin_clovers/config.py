from clovers_client import Config as CloversConfig


class ScopedConfig(CloversConfig):
    using_adapters: list[str] = ["~onebot.v11", "~qq.group", "~qq.guild", "~satori", "~uninfo"]
    priority: int = 100
    plugins: list[str] = []
    plugin_dirs: list[str] = []
    is_local: bool = True


class Config(ScopedConfig):
    clovers: ScopedConfig = ScopedConfig.sync_config()
