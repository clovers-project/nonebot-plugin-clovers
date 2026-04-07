from nonebot import require

require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")

from .main import ADAPTER


__all__ = ["ADAPTER"]
