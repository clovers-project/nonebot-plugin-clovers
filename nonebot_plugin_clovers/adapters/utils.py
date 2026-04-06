from io import BytesIO
from pathlib import Path
from datetime import datetime
from clovers_client.result import FileLike
from nonebot_plugin_clovers import is_local


def format_file_local(file):
    return file


def format_file_remote(file: FileLike) -> str | bytes:
    match file:
        case str():
            if file.startswith("http") or file.startswith("base64://"):
                return file
            return (Path(file[:7]) if file.startswith("file://") else Path(file)).read_bytes()
        case Path():
            return file.read_bytes()
        case BytesIO():
            return file.getvalue()
        case _:
            return file


def format_file(file: FileLike) -> FileLike: ...


format_file = format_file_local if is_local else format_file_remote


def format_filename(file: FileLike) -> str:
    match file:
        case str():
            if "/" in file:
                name = file.rsplit("/", 1)[-1]
                if "." not in name:
                    name += ".txt"
            elif "\\" in file:
                name = file.rsplit("\\", 1)[-1]
                if "." not in name:
                    name += ".txt"
            else:
                return f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt"
            return name
        case Path():
            return file.name
        case _:
            return f"{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt"
