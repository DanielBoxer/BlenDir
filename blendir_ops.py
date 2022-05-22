# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from .blendir_main import read_structure, archive, BlenDirError
from .structures import STRUCTURES


class BLENDIR_OT_start(Operator):
    bl_idname = "blendir.start"
    bl_label = "Create Folders"
    bl_description = "Create folder structure"

    def execute(self, context):
        props = context.scene.blendir_props
        structure = STRUCTURES.get(props.structure)

        if not bpy.data.is_saved:
            self.report({"WARNING"}, "Save the file before starting BlenDir")
            bpy.ops.wm.save_mainfile("INVOKE_AREA")
            return {"CANCELLED"}

        # if folder structure has been created before, archive it
        if props.old_path != "":
            archive(props.old_path)

        try:
            read_structure(structure)
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            archive(props.old_path)
            return {"CANCELLED"}

        self.report({"INFO"}, "Folder structure created")
        return {"FINISHED"}

    def invoke(self, context, event):
        if context.scene.blendir_props.old_path != "":
            # if folder structure has been created before, show confirmation menu
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Folder structure has already been created!", icon="ERROR")
        box.separator(factor=0)

        # multiple columns make the items closer together
        col = box.column().box().column()
        col.label(text="Press OK to recreate folder structure.")
        col.label(text="Previous folders will be moved to 'BlenDir_Archive'.")
        col.label(text="The blender file will be moved to the correct location.")


class BLENDIR_OT_reset_settings(Operator):
    bl_idname = "blendir.reset_settings"
    bl_label = "Reset Settings"
    bl_description = "Reset all settings to their default values"

    def execute(self, context):
        props = context.scene.blendir_props
        skip = ["old_path"]
        for prop in props.__annotations__.keys():
            if prop not in skip:
                props.property_unset(prop)
        return {"FINISHED"}


class BLENDIR_OT_reset(Operator):
    bl_idname = "blendir.reset"
    bl_label = "Reset BlenDir"
    bl_description = "Reset all BlenDir settings and properties to their default values"

    def execute(self, context):
        props = context.scene.blendir_props
        for prop in props.__annotations__.keys():
            props.property_unset(prop)
        return {"FINISHED"}
