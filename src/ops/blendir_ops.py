# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from ..blendir_main import (
    read_structure,
    archive,
    BlenDirError,
)
from ..utils import (
    get_active_path,
    valid_path,
    valid_filename,
    get_preferences,
    get_references,
    open_file,
)
from ..structure import import_struct
from ..bookmark import add_bookmark


class BLENDIR_OT_start(Operator):
    bl_idname = "blendir.start"
    bl_label = "Create Folders"
    bl_description = "Create folder structure"

    def execute(self, context):
        props = context.scene.blendir_props

        if not bpy.data.is_saved:
            self.report({"INFO"}, "Choose a save location")
            bpy.ops.blendir.save_blend("INVOKE_DEFAULT")
            return {"CANCELLED"}

        if get_preferences().structure == "No structures? Try adding some!":
            self.report({"ERROR"}, "Add a structure before starting BlenDir")
            return {"CANCELLED"}

        # if folder structure has been created before, archive it
        if props.old_path != "":
            try:
                archive(props.old_path)
            except BlenDirError as e:
                self.report({"ERROR"}, str(e))
                return {"CANCELLED"}

        try:
            read_structure(get_active_path())
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            archive(props.old_path)
            return {"CANCELLED"}

        self.report({"INFO"}, "Folder structure created")
        return {"FINISHED"}

    def invoke(self, context, event):
        props = context.scene.blendir_props
        if props.old_path != "" and get_preferences().show_create_warning:
            # if folder structure has been created before, show confirmation menu
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Folder structure has already been created!", icon="ERROR")
        row = box.row()
        row.alignment = "CENTER"

        box.separator(factor=0)

        # multiple columns make the items closer together
        col = box.column().box().column()
        col.label(text="Press OK to recreate folder structure.")
        col.label(text="Previous folders will be moved to 'BlenDir_Archive'.")
        col.label(text="The blender file will be moved to the correct location.")


class BLENDIR_OT_directory_browser(Operator, ImportHelper):
    bl_idname = "blendir.directory_browser"
    bl_label = "Start"
    bl_description = "Open the directory browser"

    # starting location
    directory: bpy.props.StringProperty()
    # only show folders
    filter_folder: bpy.props.BoolProperty(default=True)

    mode: bpy.props.EnumProperty(
        items=[
            ("STRUCTURE", "0", ""),
            ("BOOKMARK", "1", ""),
        ],
    )
    struct_name: bpy.props.StringProperty()

    def execute(self, context):
        path = self.filepath
        if self.mode == "STRUCTURE":
            try:
                import_struct(path, bpy.path.basename(path))
            except BlenDirError as e:
                self.report({"ERROR"}, str(e))
                return {"CANCELLED"}
            self.report({"INFO"}, f"Structure '{self.struct_name}' created")
        else:
            add_bookmark(path)

        return {"FINISHED"}

    def invoke(self, context, event):
        if self.mode == "STRUCTURE":
            # set filepath to structure name
            self.filepath = self.struct_name
        # start in current blender file location
        self.directory = bpy.data.filepath
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        box = self.layout.box()
        box.label(text="BlenDir Directory Browser", icon="FILEBROWSER")
        box.separator()
        box = box.box()
        if self.mode == "STRUCTURE":
            box.label(text="Choose a directory to import", icon="IMPORT")
            col = box.column()
            col.label(text="This directory will be the root folder")
            col.label(text="All folders inside will be added to the file")
            col.separator()
            col.label(text="Structure Name:", icon="SORTALPHA")
            if self.filepath == "":
                col.label(text="Unset")
            else:
                col.label(text=bpy.path.basename(self.filepath))
        else:
            box.label(text="Choose a directory to bookmark", icon="BOOKMARKS")
            box.label(text="Press 'Start' to add to bookmarks")
            box.separator()
            box = box.box()
            box.operator("blendir.edit_bookmarks", icon="BOOKMARKS")


class BLENDIR_OT_save_blend(Operator, ImportHelper):
    bl_idname = "blendir.save_blend"
    bl_label = "Start BlenDir"

    directory: bpy.props.StringProperty()

    def execute(self, context):
        if get_preferences().structure == "No structures? Try adding some!":
            self.report({"ERROR"}, "Add a structure before starting BlenDir")
            return {"CANCELLED"}
        if self.filepath == self.directory:
            self.report({"ERROR"}, "File name can't be empty")
            return {"CANCELLED"}
        new_filepath = valid_filename(self.filepath)
        if len(new_filepath) == 1:
            self.report({"ERROR"}, f"Invalid file name. Remove '{new_filepath}'")
            return {"CANCELLED"}
        # save in chosen location
        bpy.ops.wm.save_as_mainfile(filepath=new_filepath)
        # update the previous save location
        get_preferences().last_path = self.directory
        # code from start operator to handle exceptions
        try:
            read_structure(get_active_path())
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            archive(context.scene.blendir_props.old_path)
            return {"CANCELLED"}
        self.report({"INFO"}, f"Folder structure created")
        return {"FINISHED"}

    def invoke(self, context, event):
        # start in previous saved blender file location
        last_path = get_preferences().last_path
        if last_path != "":
            # check if the path exists
            last_path = valid_path(last_path)
        self.directory = last_path
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        box = self.layout.box()
        box.label(text="BlenDir Save Browser", icon="FILEBROWSER")
        box.separator(factor=0)
        box = box.box()
        box.label(text="1. Choose a save location!", icon="FILE_TICK")
        box.label(text="2. Enter the name of the blend file", icon="SORTALPHA")
        col = box.column()
        col.label(text="Invalid name characters: [  " + '\/:*?"<>|.' + "  ]")
        col.label(text="Adding '.blend' is not necessary.")
        col.separator()
        col = col.box().column()
        col.label(text="The 'Start BlenDir' button will:")
        col.label(text="1. Save the Blender file")
        col.label(text="2. Create folders in chosen location")


class BLENDIR_OT_reference(Operator):
    bl_idname = "blendir.reference"
    bl_label = "Reference"
    bl_description = "Reference"

    reference: bpy.props.EnumProperty(
        items=(
            ("0", "0", ""),
            ("1", "1", ""),
            ("2", "2", ""),
            ("3", "3", ""),
            ("4", "4", ""),
            ("5", "5", ""),
            ("6", "6", ""),
            ("7", "7", ""),
        )
    )

    def execute(self, context):
        refs = get_references()
        open_file(refs[1] / refs[0][int(self.reference)])
        return {"FINISHED"}
