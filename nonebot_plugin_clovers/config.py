from pydantic import BaseModel


class ConfigClovers(BaseModel):
    plugins: list[str] = []
    plugin_dirs: list[str] = ["./clovers_library/plugins"]
    adapters: list[str] = []
    adapters_dirs: list[str] = ["./clovers_library/adapters"]
