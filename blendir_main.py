# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
import pathlib
from datetime import datetime
import shutil
from sys import platform
import os
import subprocess
import json


def read_structure(structure_path):
    if structure_path.stat().st_size == 0:
        raise BlenDirError("Structure is empty")

    props = bpy.context.scene.blendir_props
    curr_blend_path = pathlib.Path(bpy.data.filepath)

    old_path = props.old_path
    if old_path == "":
        # if folder structure hasn't been created, use blender file path
        new_path = curr_blend_path.parent
    else:
        # otherwise, the blender file might have moved, so use the stored path
        new_path = pathlib.Path(old_path).parent

    # depth of -1 is the root folder
    # depth of 0 is the first folder in the structure
    previous_depth = -1
    with structure_path.open() as f:
        for line_idx, line in enumerate(f):
            # check for invalid chars immediately because they'll mess up the path
            invalid = get_invalid_char(line, skip_keywords=True)
            if invalid is not None:
                raise BlenDirError(
                    "Invalid Folder name." f" Remove '{invalid}' from line {line_idx+1}"
                )

            new_depth = line.count("\t")
            is_blend_moving = False

            if new_depth > previous_depth + 1:
                extra = new_depth - previous_depth - 1
                s = "s" if extra != 1 else ""
                raise BlenDirError(
                    "Invalid folder structure."
                    f" Line {line_idx+1} has {extra} extra tab{s}"
                )

            # remove tabs
            line = line.strip()
            # check for keywords and replace them
            if "*F" in line:
                line = line.replace("*F", curr_blend_path.stem)
            if "*B" in line:
                is_blend_moving = True
                line = line.replace("*B", "")
            if "*X" in line:
                line = line.replace("*X", props.x_input)
            if "*Y" in line:
                line = line.replace("*Y", props.y_input)
            if "*Z" in line:
                line = line.replace("*Z", props.z_input)
            if "*D" in line:
                year = datetime.now().strftime("%Y")
                month = datetime.now().strftime("%m")
                day = datetime.now().strftime("%d")
                # strip to remove " " if separator is "NONE"
                date_sep = props.date_separator.strip()
                date = ""
                for char in props.date_format:
                    if char == "Y":
                        date += year + date_sep
                    elif char == "M":
                        date += month + date_sep
                    else:
                        date += day + date_sep
                # remove last separator
                if date_sep != "NONE":
                    date = date[:-1]
                line = line.replace("*D", date)

            if line.startswith("//") or line == "":
                if line_idx == 0 and line.startswith("//"):
                    raise BlenDirError(
                        "The first line of the structure can't be a comment"
                    )
                elif line_idx == 0 and line == "":
                    raise BlenDirError("The first line of the structure can't be empty")
                else:
                    continue

            # check for invalid input
            if line_idx == 0 and (new_path / line).is_dir():
                raise BlenDirError(
                    "Root folder exists already."
                    " Change the name of the first folder in the structure"
                )
            if "*" in line:
                raise BlenDirError(
                    "Invalid Folder name." f" Remove '*' from line {line_idx+1}"
                )

            if line_idx == 0:
                # store old folder path
                props.old_path = str(new_path / line)

            if new_depth < previous_depth:
                # if a subfolder branch is ended
                new_path = new_path.parents[previous_depth - new_depth]
            elif new_depth == previous_depth:
                # if the next folder is in the same location
                new_path = new_path.parent

            # when adding a subfolder, it's added to the path with no changes needed
            new_path /= line
            previous_depth = new_depth

            # make folder
            new_path.mkdir()

            if is_blend_moving:
                move_blend(new_path)


def move_blend(new_path):
    curr_blend_path = pathlib.Path(bpy.data.filepath)
    new_blend_path = new_path / curr_blend_path.name

    # the backups have to be moved before the blender file
    # this is because it will create a backup when saving
    for path in curr_blend_path.parent.iterdir():
        # move all the backup files (.blend1, .blend2 ...)
        s = path.suffix.split(".blend")
        if (
            path.is_file()
            and len(s) > 1
            and s[-1].isdigit()
            and int(s[-1]) in range(1, 33)  # there can only be 32 backups
            and curr_blend_path.stem == path.stem
        ):
            # the current path is a blender backup file of the current file
            path.rename(new_blend_path.parent / path.name)

    try:
        # move blender file to the new location
        curr_blend_path.rename(new_blend_path)
    except FileNotFoundError as e:
        raise BlenDirError(
            "Error moving the Blender file while archiving. Try reopening the file"
        ) from e
    # save as, so the filepath is changed in the blender file
    bpy.ops.wm.save_as_mainfile(filepath=str(new_blend_path))


def archive(old_path):
    old_path = pathlib.Path(old_path)
    # check if old path exists
    # also, if the first line is empty, the path would be ".", the current path
    # so this has to be skipped as well
    if old_path.is_dir() and str(old_path) != ".":
        root_path = old_path.parent
        # check if blender file is in root folder already
        if root_path != pathlib.Path(bpy.data.filepath).parent:
            # move blender files to root folder
            move_blend(root_path)

        # folder where all old structures are moved to
        archive = root_path / "BlenDir_Archive"
        archive.mkdir(exist_ok=True)
        suffix = 0
        for path in archive.iterdir():
            # check if there are other old structures
            # the new suffix will be one greater than the previous
            s = path.name.split("_")
            if path.is_dir() and len(s) > 1 and s[0].isdigit() and int(s[0]) >= suffix:
                suffix = int(s[0]) + 1

        new_path = archive / (f"{suffix}_{old_path.stem}")
        old_path.rename(new_path)


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


def open_file(file):
    if platform == "win32":
        os.startfile(file)
    elif platform == "darwin":
        subprocess.call(("open", str(file)))
    else:
        subprocess.call(("xdg-open", str(file)))


def open_struct(file):
    props = bpy.context.scene.blendir_props
    if not "No structures? Try adding some!" in props.struct_items:
        # open file in default text editor
        open_file(file)
    else:
        raise BlenDirError("No structures to edit")


def open_path(path):
    path = pathlib.Path(path).parent
    # open path in file browser
    open_file(path)


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
    props = context.scene.blendir_props
    icon = props.struct_icon
    items = []
    for item_idx, item in enumerate(props.struct_items):
        items.append((item, item, "", icon, item_idx))
    return items


def structs_add_value(value):
    # add to the structure enum
    props = bpy.context.scene.blendir_props
    props.struct_items.append(value)
    msg = "No structures? Try adding some!"
    if msg in props.struct_items:
        props.struct_items.remove(msg)
        props.struct_icon = "TRIA_RIGHT"
    # set enum to the new structure name
    bpy.context.scene.blendir_props.structure = value


def structs_remove_value(value):
    props = bpy.context.scene.blendir_props
    if not "No structures? Try adding some!" in props.struct_items:
        # delete structure file
        get_active_path().unlink()
        props.struct_items.remove(value)
        # set enum to index 0
        props = bpy.context.scene.blendir_props
        props.property_unset("structure")
        structs_add_empty()
    else:
        raise BlenDirError("No structures to remove")


def import_struct(path):
    struct_name = bpy.context.scene.blendir_props.struct_name
    if struct_name == "":
        raise BlenDirError("The structure name can't be blank")
    invalid = get_invalid_char(struct_name)
    if invalid is not None:
        raise BlenDirError("Invalid structure name." f" Remove '{invalid}' from name")
    if get_active_path(struct_name).is_file():
        raise BlenDirError(f"Structure '{struct_name}' already exists")

    with get_active_path(struct_name).open("w") as f:
        initial_path = pathlib.Path(path)
        initial_depth = len(initial_path.parents)
        # travel through all folders
        for dir in os.walk(initial_path):
            dir_path = pathlib.Path(dir[0])
            new_depth = len(dir_path.parents)
            # the depth is the amount of tabs the folder should have
            curr_depth = new_depth - initial_depth
            f.write("\t" * curr_depth + dir_path.stem + "\n")
    structs_add_value(struct_name)
    open_struct(get_active_path())


def structs_add_empty():
    props = bpy.context.scene.blendir_props
    if len(props.struct_items) == 0:
        props.struct_items.append("No structures? Try adding some!")
        props.struct_icon = "ERROR"


def load_startup():
    try:
        path = pathlib.Path(__file__).resolve().parent / "startup.json"
        with open(path, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        # default settings
        data = {
            "structure": 0,
            "x_input": "",
            "y_input": "",
            "z_input": "",
            "date_format": "YMD",
            "date_separator": "-",
            "show_del_warning": True,
            "show_create_warning": True,
            "close_sidebar": False,
            "open_button": "BLEND",
        }
        write_json(data)
        return data


def save_prefs():
    props = bpy.context.scene.blendir_props
    data = {}
    skip = ["old_path", "struct_items", "struct_icon", "struct_name"]
    for prop in props.__annotations__.keys():
        if prop not in skip:
            if prop == "structure":
                # save int value of structure instead of string id
                # default value must be int for this property
                data[prop] = props.get(prop)
            else:
                # all properties must be initialized with the correct type in the JSON file
                data[prop] = getattr(props, prop)
    write_json(data)


def write_json(data):
    path = pathlib.Path(__file__).resolve().parent / "startup.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def get_invalid_char(line, skip_keywords=False):
    invalid = '\/:*?"<>|.'
    if skip_keywords:
        if line.startswith("//"):
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


def get_dir_path():
    return pathlib.Path(__file__).resolve().parent


def get_struct_path():
    return get_dir_path() / "structures"


def get_active_path(input_struct=None):
    if input_struct is not None:
        return get_struct_path() / f"blendir_{input_struct}.txt"
    props = bpy.context.scene.blendir_props
    return get_struct_path() / f"blendir_{props.structure}.txt"


# custom exception
class BlenDirError(ValueError):
    pass
