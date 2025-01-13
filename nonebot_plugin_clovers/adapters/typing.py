from collections.abc import AsyncGenerator
from clovers import Result
from typing import TypedDict
from io import BytesIO

type ListMessage = list[Result]
type SegmentedMessage = AsyncGenerator[Result, None]
type UrlOrData = str | bytes | BytesIO


class GroupMessage(TypedDict):
    group_id: str
    data: Result


class PrivateMessage(TypedDict):
    user_id: str
    data: Result
