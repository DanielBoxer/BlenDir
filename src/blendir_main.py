# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
import pathlib
import os
from .utils import (
    get_invalid_char,
    get_preferences,
    get_datetime,
)


def read_structure(structure_path):
    if structure_path.stat().st_size == 0:
        raise BlenDirError("Structure is empty")

    props = bpy.context.scene.blendir_props
    curr_blend_path = pathlib.Path(bpy.data.filepath)
    bpy.context.scene.blendir_bookmarks.clear()

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
            store_bookmark = False
            store_ref_path = False
            set_render_path = False

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
                line = line.replace("*X", get_preferences().x_input)
            if "*Y" in line:
                line = line.replace("*Y", get_preferences().y_input)
            if "*Z" in line:
                line = line.replace("*Z", get_preferences().z_input)
            if "*D" in line:
                date = get_datetime()
                line = line.replace("*D", date)
            if "*M" in line:
                line = line.replace("*M", "")
                store_bookmark = True
            if "*R" in line:
                line = line.replace("*R", "")
                store_ref_path = True
            if "*O" in line:
                line = line.replace("*O", "")
                set_render_path = True

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
                # store old root folder path
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

            if new_path.is_dir():
                raise BlenDirError(
                    f"Folder {line} exists already. Change line {line_idx+1}"
                )

            if store_bookmark:
                new_bookmark = bpy.context.scene.blendir_bookmarks.add()
                new_bookmark.path = str(new_path)
            if store_ref_path:
                props.reference_path = str(new_path)
            if set_render_path:
                # add separator because it gets removed when casting to string
                render_path = str(new_path) + os.sep
                bpy.context.scene.render.filepath = render_path
                props.render_path = render_path

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


def make_render_folders():
    prefs = get_preferences()
    render_path = bpy.context.scene.blendir_props.render_path
    if render_path == "":
        default_render_path = bpy.context.scene.render.filepath
        bpy.context.scene.blendir_props.render_path = default_render_path
        render_path = default_render_path
    # the default output path is relative so it must be made absolute
    render_path = pathlib.Path(render_path).resolve()
    if prefs.make_frames_folder:
        render_path /= "Frames"
        render_path.mkdir(exist_ok=True)
    if prefs.make_animation_folders:
        num = 0
        # the new folder will be named one number higher than the last
        for path in render_path.iterdir():
            if path.is_dir():
                stem = path.stem
                if stem.isdigit():
                    if int(stem) >= num:
                        num = int(stem) + 1
        render_path /= str(num)
        render_path.mkdir()
    return str(render_path) + os.sep


# custom exception
class BlenDirError(ValueError):
    pass
