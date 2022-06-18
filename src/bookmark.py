# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from .blendir_main import BlenDirError
from .utils import get_dir_path, open_file


def add_bookmark(bookmark):
    path = get_dir_path() / "bookmarks.txt"
    with path.open("a") as f:
        f.write(bookmark + "\n")


def get_bookmarks():
    bookmarks = []
    path = get_dir_path() / "bookmarks.txt"
    if path.is_file():
        with path.open("r") as f:
            for line in f:
                bookmarks.append(line.strip())
    return bookmarks


def open_bookmarks():
    path = get_dir_path() / "bookmarks.txt"
    if path.is_file():
        open_file(path)
    else:
        raise BlenDirError("No bookmarks to edit, try adding some with the browser")


class BLENDIR_PG_bookmark(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty()
