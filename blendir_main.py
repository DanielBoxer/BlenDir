# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
import pathlib
from datetime import datetime


def read_structure(structure):
    props = bpy.context.scene.blendir_props
    curr_blend_path = pathlib.Path(bpy.data.filepath)
    file_stem = curr_blend_path.stem

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
    for line_idx, line in enumerate(structure):
        new_depth = line.count("\t")
        is_blend_moving = False

        # remove tabs
        line = line.strip()
        # check for keywords and replace them
        if "*F" in line:
            line = line.replace("*F", file_stem)
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

        if line_idx == 0:
            # store old folder path
            props.old_path = str(new_path / line)

        # check for invalid input
        if line == "":
            raise BlenDirError(f"Invalid folder structure. Line {line_idx+1} is empty")

        if new_depth > previous_depth + 1:
            extra = new_depth - previous_depth - 1
            s = "s" if extra != 1 else ""
            raise BlenDirError(
                f"Invalid folder structure. Line {line_idx+1} has {extra} extra tab{s}"
            )

        if line_idx == 0 and (new_path / line).is_dir():
            raise BlenDirError(
                "Root folder exists already."
                " Change the name of the first folder in the structure"
            )

        invalid = '\/:*?"<>|'
        # check for invalid characters
        if any(char in line for char in invalid):
            # if found, check which one it is
            for c1 in line:
                for c2 in invalid:
                    if c1 == c2:
                        raise BlenDirError(
                            f"Invalid Folder name. Remove '{c1}' from line {line_idx+1}"
                        )

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

    # move all the backup files (.blend1, .blend2 ...)
    for path in curr_blend_path.parent.iterdir():
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

    # move blender file to this location
    # if the blend file is moved first, when it's saved, it will create a backup
    # this will cause an error when the old backups are moved
    curr_blend_path.rename(new_blend_path)
    # save as, so the filepath is changed in the blender file
    bpy.ops.wm.save_as_mainfile(filepath=str(new_blend_path))


def archive(old_path):
    old_path = pathlib.Path(old_path)
    # check if old path exists
    if old_path.is_dir():
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


# custom exception
class BlenDirError(ValueError):
    pass
