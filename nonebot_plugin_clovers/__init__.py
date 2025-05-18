from importlib import import_module
from nonebot import logger
from clovers import Adapter
from .clovers import get_client
from .config import __config__
from .adapters.typing import Handler

for import_name in __config__.using_adapters:
    try:
        module = import_module(import_name)
        adapter = getattr(module, "__adapter__", None)
        assert adapter and isinstance(adapter, Adapter), f"{import_name} adapter is not valid"
        handler = getattr(module, "handler", None)
        assert handler and isinstance(handler, Handler), f"{import_name} handler is not valid"
    except Exception:
        logger.exception(f"{import_name} 加载失败")
        continue
    get_client().register_adapter(adapter, handler)
