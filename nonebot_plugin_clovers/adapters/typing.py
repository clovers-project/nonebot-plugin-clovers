from pathlib import Path
from collections.abc import AsyncGenerator
from typing import TypedDict, Protocol, runtime_checkable
from io import BytesIO
from clovers import Result
from nonebot.matcher import Matcher
from nonebot.adapters import Bot as BaseBot, Event as BaseEvent

type ListMessage = list[Result]
type SegmentedMessage = AsyncGenerator[Result, None]
type FileLike = str | bytes | BytesIO | Path


class GroupMessage(TypedDict):
    group_id: str
    data: Result


class PrivateMessage(TypedDict):
    user_id: str
    data: Result


@runtime_checkable
class Handler[Bot: BaseBot, Event: BaseEvent](Protocol):
    async def __call__(self, bot: Bot, event: Event, matcher: Matcher) -> None: ...
