from pathlib import Path
from collections import deque
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna.uniseg import UniMessage, Target
from nonebot_plugin_uninfo import get_session, Session
from clovers_client.result import FileLike, SequenceMessage, SegmentedMessage, Result
from nonebot_plugin_clovers.adapters.utils import format_file, format_filename


def image2message(message: FileLike):
    message = format_file(message)
    match message:
        case str():
            return UniMessage.image(url=message)
        case Path():
            return UniMessage.image(path=message)
        case _:
            return UniMessage.image(raw=message)


def voice2message(message: FileLike):
    message = format_file(message)
    match message:
        case str():
            return UniMessage.voice(url=message)
        case Path():
            return UniMessage.voice(path=message)
        case _:
            return UniMessage.voice(raw=message)


def video2message(message: FileLike):
    message = format_file(message)
    match message:
        case str():
            return UniMessage.video(url=message)
        case Path():
            return UniMessage.video(path=message)
        case _:
            return UniMessage.video(raw=message)


def file2message(message: FileLike):
    filename = format_filename(message)
    message = format_file(message)
    match message:
        case str():
            return UniMessage.file(url=message, name=filename)
        case Path():
            return UniMessage.file(path=message, name=filename)
        case _:
            return UniMessage.file(raw=message, name=filename)


def list2message(message: SequenceMessage) -> UniMessage:
    unimsg = UniMessage()
    for seg in message:
        match seg.key:
            case "text":
                unimsg = unimsg.text(seg.data)
            case "image":
                unimsg += image2message(seg.data)
            case "at":
                unimsg = unimsg.at(seg.data)
                unimsg = unimsg.text(" ")
    return unimsg


def to_message(result: Result) -> UniMessage | None:
    match result.key:
        case "at":
            return UniMessage.at(result.data)
        case "text":
            return UniMessage.text(result.data)
        case "image":
            return image2message(result.data)
        case "list":
            return list2message(result.data)
        case "voice":
            return voice2message(result.data)
        case "video":
            return video2message(result.data)
        case "file":
            return file2message(result.data)


async def send_segmented_result(result: SegmentedMessage, event: Target | Event, bot: Bot):
    async for seg in result:
        match seg.key:
            case "at":
                await UniMessage.at(seg.data).send(event, bot)
            case "text":
                await UniMessage.text(seg.data).send(event, bot)
            case "image":
                await image2message(seg.data).send(event, bot)
            case "list":
                await list2message(seg.data).send(event, bot)
            case "video":
                await video2message(seg.data).send(event, bot)
            case "voice":
                await voice2message(seg.data).send(event, bot)
            case "file":
                await file2message(seg.data).send(event, bot)


async def send_result(target: Target, result: Result, bot: Bot):
    if result.key == "segmented":
        await send_segmented_result(result.data, target, bot)
    elif unimsg := to_message(result):
        await target.send(unimsg, bot)


type CacheDeque[Item] = deque[tuple[Event, Item]]


_session_chche_deque: CacheDeque[Session] = deque(maxlen=10)
_unimsg_cache_deque: CacheDeque[UniMessage] = deque(maxlen=10)


def find_from_deque[Item](event: Event, queue: CacheDeque[Item]) -> Item | None:
    for item in queue:
        if item[0] == event:
            return item[1]


async def get_current_session(bot: Bot, event: Event):
    global _session_chche_deque
    session = find_from_deque(event, _session_chche_deque)
    if session is None:
        session = await get_session(bot, event)
        if session is not None:
            _session_chche_deque.appendleft((event, session))
    return session


def get_current_unimsg(bot: Bot, event: Event) -> UniMessage:
    global _unimsg_cache_deque
    unimsg = find_from_deque(event, _unimsg_cache_deque)
    if unimsg is None:
        unimsg = UniMessage.of(event.get_message())
        _unimsg_cache_deque.appendleft((event, unimsg))
    return unimsg
