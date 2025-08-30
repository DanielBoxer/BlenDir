# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import pathlib
import os
import shutil
from .blendir_main import BlenDirError
from .utils import (
    get_preferences,
    get_invalid_char,
    get_struct_path,
    open_file,
    get_active_path,
)


def new_struct(name, use_template):
    dir = get_struct_path()
    dst = dir / f"blendir_{name}.txt"
    if dst.is_file():
        raise BlenDirError("Structure exists already. Try a different structure name")

    if use_template == "TEMPLATE":
        # copy new.txt template file
        src = dir / "new.txt"
        if not src.is_file():
            raise BlenDirError(
                "Template file not found. Use 'Empty File' to create the structure"
            )
        shutil.copyfile(src, dst)
    else:
        # make blank file
        open(dst, "w").close()

    structs_add_value(name)
    open_struct(dst)


def open_struct(file):
    if "No structures? Try adding some!" not in get_preferences().struct_items:
        # open file in default text editor
        open_file(file)
    else:
        raise BlenDirError("No structures to edit")


def init_structs():
    # add all structure files currently saved
    items = []
    icon = "TRIA_RIGHT"
    for struct in get_struct_path().iterdir():
        name = struct.stem.split("blendir_")
        if len(name) > 1:
            items.append(name[1])
    if len(items) == 0:
        icon = "ERROR"
        items.append("No structures? Try adding some!")

    return items, icon


def update_structs(scene, context):
    # scene and context params are needed for this callback function
    prefs = get_preferences()
    icon = prefs.struct_icon
    items = []
    for item_idx, item in enumerate(prefs.struct_items):
        items.append((item, item, "", icon, item_idx))
    return items


def structs_add_value(value):
    # add to the structure enum
    prefs = get_preferences()
    prefs.struct_items.append(value)
    msg = "No structures? Try adding some!"
    if msg in prefs.struct_items:
        prefs.struct_items.remove(msg)
        prefs.struct_icon = "TRIA_RIGHT"
    # set enum to the new structure name
    prefs.structure = value


def structs_remove_value(value):
    prefs = get_preferences()
    if "No structures? Try adding some!" not in prefs.struct_items:
        # delete structure file
        get_active_path().unlink()
        prefs.struct_items.remove(value)
        # set enum to index 0
        prefs.property_unset("structure")
        structs_add_empty()
    else:
        raise BlenDirError("No structures to remove")


def import_struct(path, struct_name):
    if struct_name == "":
        raise BlenDirError("The structure name can't be blank")
    invalid = get_invalid_char(struct_name)
    if invalid is not None:
        raise BlenDirError("Invalid structure name." f" Remove '{invalid}' from name")
    if get_active_path(struct_name).is_file():
        raise BlenDirError(f"Structure '{struct_name}' already exists")

    with get_active_path(struct_name).open("w") as f:
        # remove structure name from path
        path = pathlib.Path(path).parent
        initial_depth = len(path.parents)
        # travel through all folders
        for dir in os.walk(path):
            dir_path = pathlib.Path(dir[0])
            new_depth = len(dir_path.parents)
            # the depth is the amount of tabs the folder should have
            curr_depth = new_depth - initial_depth
            f.write("\t" * curr_depth + dir_path.stem + "\n")

        # add keyword information
        template_path = get_struct_path() / "new.txt"
        if template_path.is_file():
            f.write("\n")
            f.write("\n")
            with template_path.open("r") as template:
                # skip the example structure
                for line in template:
                    if "Keywords (case sensitive)" in line:
                        f.write(line)
                        break
                    else:
                        template.readline()
                # write keyword information
                for line in template:
                    f.write(line)

    structs_add_value(struct_name)
    open_struct(get_active_path())


def structs_add_empty():
    prefs = get_preferences()
    if len(prefs.struct_items) == 0:
        prefs.struct_items.append("No structures? Try adding some!")
        prefs.struct_icon = "ERROR"
