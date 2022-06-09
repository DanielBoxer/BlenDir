# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from ..blendir_main import BlenDirError
from ..utils import get_invalid_char, get_active_path, get_preferences
from ..structure import open_struct, new_struct, structs_remove_value


class BLENDIR_OT_new_structure(Operator):
    bl_idname = "blendir.new_structure"
    bl_label = "New Structure"
    bl_description = "Make a new folder structure file"

    use_template: bpy.props.EnumProperty(
        name="File",
        items=[
            (
                "TEMPLATE",
                "Use Template",
                (
                    "The new file will have a template and information about "
                    "how to make the structure"
                ),
            ),
            ("EMPTY", "Empty File", "Create an empty structure with no comments"),
        ],
    )
    struct_name: bpy.props.StringProperty(
        name="Structure Name",
        description="Enter the name of the structure",
    )

    def execute(self, context):
        file_name = self.struct_name
        # check for invalid input
        if file_name == "":
            self.report({"ERROR"}, "The structure name can't be blank")
            return {"CANCELLED"}
        invalid = get_invalid_char(file_name)
        if invalid is not None:
            self.report(
                {"ERROR"}, "Invalid structure name." f" Remove '{invalid}' from name"
            )
            return {"CANCELLED"}

        try:
            new_struct(file_name, self.use_template)
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        self.report({"INFO"}, f"Structure '{file_name}' created")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.struct_name = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        row = box.row()
        row.prop(self, "use_template", expand=True)
        box.prop(self, "struct_name", icon="SORTALPHA")


class BLENDIR_OT_edit_structure(Operator):
    bl_idname = "blendir.edit_structure"
    bl_label = "Edit Structure"
    bl_description = (
        "Edit the active folder structure file."
        " This will open it in the default text editor"
    )

    def execute(self, context):
        try:
            open_struct(get_active_path())
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Editing structure '{get_preferences().structure}'")
        return {"FINISHED"}


class BLENDIR_OT_delete_structure(Operator):
    bl_idname = "blendir.delete_structure"
    bl_label = "Delete Structure"
    bl_description = "Delete the active folder structure file"

    confirm: bpy.props.StringProperty(name="", description="Enter 'delete' to confirm")

    def execute(self, context):
        struct_name = get_preferences().structure
        if self.confirm == "delete" or not get_preferences().show_del_warning:
            try:
                structs_remove_value(struct_name)
            except BlenDirError as e:
                self.report({"ERROR"}, str(e))
                return {"CANCELLED"}
        else:
            self.report({"INFO"}, "Deletion cancelled")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Structure '{struct_name}' deleted")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.confirm = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if get_preferences().show_del_warning:
            box = layout.box()
            box.label(text="Deletion is permanent!", icon="ERROR")
            box.label(text="Files will NOT be moved to the recycle bin / trash!")
            row = box.box().row()
            row.label(text="Enter 'delete' to continue:")
            row.prop(self, "confirm", icon="TRASH")
        else:
            box = layout.box()
            box.label(text="Press OK to delete structure", icon="ERROR")


class BLENDIR_OT_import_structure(Operator):
    bl_idname = "blendir.import_structure"
    bl_label = "Import Structure"
    bl_description = (
        "Import a directory as a folder structure file."
        " This will generate a file with the structure of the chosen directory"
    )

    struct_name: bpy.props.StringProperty(
        name="Structure Name",
        description="Enter the name of the structure",
    )

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        box = layout.box()
        box.label(
            text="Generate a folder structure file from a directory!",
            icon="COLLECTION_NEW",
        )
        box.separator(factor=0)

        col = box.box().column()
        col.label(text="The chosen directory will be the root folder.")
        col.label(text="All folders inside the directory will be added to the file.")

        col.separator(factor=2)
        row = col.row()
        row.prop(self, "struct_name", icon="SORTALPHA")

        row = col.row()
        row.scale_y = 2
        row.operator_context = "INVOKE_DEFAULT"
        dir_browser = row.operator(
            "blendir.directory_browser",
            text="Open Directory Browser",
            icon="FILEBROWSER",
        )
        dir_browser.mode = "STRUCTURE"
        dir_browser.struct_name = self.struct_name
