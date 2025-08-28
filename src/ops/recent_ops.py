# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy

from ..recent import get_recent
from ..utils import get_preferences, get_recent_path, get_references, open_file


class BLENDIR_OT_open_recent(bpy.types.Operator):
    bl_idname = "blendir.open_recent"
    bl_label = "Open Recent"
    bl_description = "Open recent project"

    recent_idx: bpy.props.IntProperty()

    def execute(self, context):
        bpy.ops.wm.open_mainfile(filepath=get_recent()[self.recent_idx])
        if get_preferences().autoload_refs:
            try:
                refs = get_references()
            except FileNotFoundError:
                self.report({"ERROR"}, "Project references could not be loaded")
                return {"CANCELLED"}
            # open up to 8 references
            if refs[1] != "":
                for ref_idx, ref in enumerate(refs[0]):
                    if ref_idx > 7:
                        break
                    open_file(refs[1] / ref)
        return {"FINISHED"}

    def invoke(self, context, event):
        if bpy.data.is_dirty:
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="There are unsaved changes!", icon="ERROR")
        box.label(text="Press OK to discard recent work and continue.")


class BLENDIR_OT_edit_recent(bpy.types.Operator):
    bl_idname = "blendir.edit_recent"
    bl_label = "Edit Recent Projects"
    bl_description = "Edit recent projects"

    def execute(self, context):
        path = get_recent_path()
        if path.is_file():
            open_file(path)
        else:
            self.report({"ERROR"}, "No recent projects")
            return {"CANCELLED"}
        return {"FINISHED"}
