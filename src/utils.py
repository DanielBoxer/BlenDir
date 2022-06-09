# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
import pathlib
import datetime
import os
import sys
import subprocess


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


def get_struct_path():
    return get_dir_path() / "structures"


def get_active_path(input_struct=None):
    if input_struct is not None:
        return get_struct_path() / f"blendir_{input_struct}.txt"
    return get_struct_path() / f"blendir_{get_preferences().structure}.txt"


def get_preferences():
    return bpy.context.preferences.addons[get_dir_path().stem].preferences
