# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import datetime
import os
import pathlib
import shutil
import subprocess
import sys

import bpy


def get_invalid_char(line, skip_keywords=False):
    invalid = '\/:*?"<>|.'
    if skip_keywords:
        if line.strip().startswith("//"):
            return None
        invalid = invalid.replace("*", "")
    # check for invalid characters
    if any(char in line for char in invalid):
        # if found, check which one it is
        for c1 in line:
            for c2 in invalid:
                if c1 == c2:
                    return c1
    else:
        return None


def valid_path(path):
    path = pathlib.Path(path)
    # check if path exists
    if not path.is_dir():
        # return the next existing parent
        for parent in path.parents:
            if parent.exists():
                return str(parent)
    return str(path)


def valid_filename(path):
    path = pathlib.Path(path)
    stem = path.stem
    invalid = get_invalid_char(stem)
    if invalid is not None:
        return invalid
    new_path = str(path.parent / (stem + ".blend"))
    return new_path


def get_datetime(get_time=False):
    prefs = get_preferences()
    output = ""
    # strip to remove " " if separator is "NONE"
    date_sep = prefs.date_separator.strip()

    dt = datetime.datetime
    for char_idx, char in enumerate(prefs.date_format):
        if char == "Y":
            output += dt.now().strftime("%Y")
        elif char == "M":
            output += dt.now().strftime("%m")
        else:
            output += dt.now().strftime("%d")
        if char_idx < 2:
            output += date_sep

    if get_time:
        output += date_sep
        if prefs.time_format == "HMS":
            output += dt.now().strftime("%H") + date_sep
        output += dt.now().strftime("%M") + date_sep
        output += dt.now().strftime("%S")

    return output


def get_references():
    ref_path = bpy.context.scene.blendir_props.reference_path
    references = []
    if ref_path != "":
        ref_path = pathlib.Path(ref_path)
        for ref in os.listdir(ref_path):
            if (ref_path / ref).is_file():
                references.append(ref)
    return references, ref_path


def reset_props(context=bpy.context):
    props = context.scene.blendir_props
    props.old_path = ""
    props.reference_path = ""
    props.render_path = ""
    props.bookmark_page = 0


def open_file(file):
    platform = sys.platform
    if platform == "win32":
        os.startfile(file)
    elif platform == "darwin":
        subprocess.call(("open", str(file)))
    else:
        subprocess.call(("xdg-open", str(file)))


def open_path(path, open_folder=False):
    path = pathlib.Path(path)
    if not open_folder:
        path = path.parent
    # open path in file browser
    open_file(path)


def get_file_path():
    return pathlib.Path(__file__)


def get_dir_path():
    return get_file_path().parents[1]


def get_addon_name():
    return get_dir_path().stem


def get_root_package():
    parts = __package__.split(".")
    return ".".join(parts[:3])


def get_extension_dir_path():
    if bpy.app.version < (4, 2, 0):
        return get_dir_path()

    blendir_folder = pathlib.Path(
        bpy.utils.extension_path_user(get_root_package(), create=True)
    )
    struct_dest = blendir_folder / "structures"
    if not struct_dest.exists():
        # copy structures folder to the safe extension folder
        struct_src = get_dir_path() / "structures"
        shutil.copytree(struct_src, struct_dest, dirs_exist_ok=True)

    return blendir_folder


def get_struct_path():
    return get_extension_dir_path() / "structures"


def get_recent_path():
    return get_extension_dir_path() / "recent.txt"


def get_panel_path():
    return get_extension_dir_path() / "panel_location.txt"


def get_bookmark_path():
    return get_extension_dir_path() / "bookmarks.txt"


def get_active_path(input_struct=None):
    if input_struct is not None:
        return get_struct_path() / f"blendir_{input_struct}.txt"
    return get_struct_path() / f"blendir_{get_preferences().structure}.txt"


def get_addon_id():
    if bpy.app.version >= (4, 2, 0):
        return get_root_package()
    return get_addon_name()


def get_preferences():
    return bpy.context.preferences.addons[get_addon_id()].preferences


def get_panel_category():
    path = get_panel_path()

    DEFAULT_PANEL = "BlenDir"
    if not path.is_file():
        return DEFAULT_PANEL

    with path.open("r") as f:
        return f.read().strip()


def set_panel_category(location):
    path = get_panel_path()
    with path.open("w") as f:
        f.write(location)
