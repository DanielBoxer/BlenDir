# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
import pathlib
from .blendir_main import (
    read_structure,
    archive,
    get_active_path,
    new_struct,
    get_invalid_char,
    open_struct,
    structs_remove_value,
    open_blend,
    import_struct,
    save_prefs,
    valid_path,
    valid_filename,
    BlenDirError,
)


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

        if props.structure == "No structures? Try adding some!":
            self.report({"ERROR"}, "Add a structure before starting BlenDir")
            return {"CANCELLED"}

        # if folder structure has been created before, archive it
        if props.old_path != "":
            archive(props.old_path)

        try:
            read_structure(get_active_path())
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            archive(props.old_path)
            return {"CANCELLED"}

        if props.close_sidebar:
            context.space_data.show_region_ui = False
        self.report({"INFO"}, "Folder structure created")
        return {"FINISHED"}

    def invoke(self, context, event):
        props = context.scene.blendir_props
        if props.old_path != "" and props.show_create_warning:
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

    def execute(self, context):
        file_name = context.scene.blendir_props.struct_name
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
        context.scene.blendir_props.struct_name = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        props = context.scene.blendir_props

        box = layout.box()
        row = box.row()
        row.prop(self, "use_template", expand=True)
        box.prop(props, "struct_name", icon="SORTALPHA")


class BLENDIR_OT_edit_structure(Operator):
    bl_idname = "blendir.edit_structure"
    bl_label = "Edit Structure"
    bl_description = (
        "Edit the active folder structure file."
        " This will open it in the default text editor"
    )

    def execute(self, context):
        props = context.scene.blendir_props
        try:
            open_struct(get_active_path())
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Editing structure '{props.structure}'")
        return {"FINISHED"}


class BLENDIR_OT_delete_structure(Operator):
    bl_idname = "blendir.delete_structure"
    bl_label = "Delete Structure"
    bl_description = "Delete the active folder structure file"

    confirm: bpy.props.StringProperty(name="", description="Enter 'delete' to confirm")

    def execute(self, context):
        props = context.scene.blendir_props
        struct_name = props.structure

        if props.confirm == "delete" or not props.show_del_warning:
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
        context.scene.blendir_props.confirm = ""
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        props = context.scene.blendir_props

        if props.show_del_warning:
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

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        props = context.scene.blendir_props
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
        row.prop(props, "struct_name", icon="SORTALPHA")

        row = col.row()
        row.scale_y = 2
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "blendir.directory_browser",
            text="Open Directory Browser",
            icon="FILEBROWSER",
        )


class BLENDIR_OT_directory_browser(Operator, ImportHelper):
    bl_idname = "blendir.directory_browser"
    bl_label = "Create Structure"
    bl_description = "Open the directory browser"

    # starting location
    directory: bpy.props.StringProperty()
    # only show folders
    filter_folder: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        try:
            import_struct(self.filepath)
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        props = context.scene.blendir_props
        self.report({"INFO"}, f"Structure '{props.struct_name}' created")
        props.struct_name = ""
        return {"FINISHED"}

    def invoke(self, context, event):
        # clear initial path
        self.filepath = ""
        # start in current blender file location
        self.directory = bpy.data.filepath
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        props = context.scene.blendir_props
        box = layout.box()
        box.label(text="BlenDir Directory Browser", icon="FILEBROWSER")
        box.separator(factor=0)
        box = box.box()
        box.label(text="Change Structure Name:")
        box.prop(props, "struct_name", text="", icon="SORTALPHA")


class BLENDIR_OT_save_blend(Operator, ImportHelper):
    bl_idname = "blendir.save_blend"
    bl_label = "Start BlenDir"

    directory: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.blendir_props
        if props.structure == "No structures? Try adding some!":
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
        context.preferences.addons[
            pathlib.Path(__file__).resolve().parent.stem
        ].preferences.last_path = self.directory
        # code from start operator to handle exceptions
        try:
            read_structure(get_active_path())
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            archive(props.old_path)
            return {"CANCELLED"}
        if props.close_sidebar:
            context.space_data.show_region_ui = False
        self.report({"INFO"}, f"Folder structure created")
        return {"FINISHED"}

    def invoke(self, context, event):
        # start in previous saved blender file location
        last_path = context.preferences.addons[
            pathlib.Path(__file__).resolve().parent.stem
        ].preferences.last_path
        if last_path != "":
            # check if the path exists
            last_path = valid_path(last_path)
        self.directory = last_path
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="BlenDir File Browser", icon="FILEBROWSER")
        box.separator(factor=0)
        box = box.box()
        box.label(text="Choose a save location!", icon="FILE_TICK")
        col = box.column()
        col.label(text="Invalid name characters: [  " + '\/:*?"<>|.' + "  ]")
        col.label(text="Adding '.blend' is not necessary.")
        col.separator()
        col = col.box().column()
        col.label(text="The 'Start BlenDir' button will:")
        col.label(text="1. Save the Blender file")
        col.label(text="2. Create folders in chosen location")


class BLENDIR_OT_open_blend(Operator):
    bl_idname = "blendir.open_blend"
    bl_label = "Open Blender File"
    bl_description = "Open the location of the current blender file in the file browser"

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({"ERROR"}, "The Blender file must be saved")
            return {"CANCELLED"}
        open_blend(bpy.data.filepath)
        return {"FINISHED"}


class BLENDIR_OT_save_settings(Operator):
    bl_idname = "blendir.save_settings"
    bl_label = "Save Settings"
    bl_description = (
        "All settings will be saved."
        " These settings will be loaded when Blender is started"
    )

    def execute(self, context):
        save_prefs()
        self.report({"INFO"}, "Blendir settings saved")
        return {"FINISHED"}


class BLENDIR_OT_reset_settings(Operator):
    bl_idname = "blendir.reset_settings"
    bl_label = "Reset Settings"
    bl_description = "Reset all settings to their default values"

    def execute(self, context):
        props = context.scene.blendir_props
        skip = ["old_path", "struct_items", "struct_icon"]
        for prop in props.__annotations__.keys():
            if prop not in skip:
                props.property_unset(prop)
        self.report({"INFO"}, "BlenDir settings reset")
        return {"FINISHED"}


class BLENDIR_OT_reset(Operator):
    bl_idname = "blendir.reset"
    bl_label = "Reset BlenDir"
    bl_description = "Reset all BlenDir settings and properties to their default values"

    def execute(self, context):
        props = context.scene.blendir_props
        for prop in props.__annotations__.keys():
            props.property_unset(prop)
        self.report({"INFO"}, "BlenDir settings and properties reset")
        return {"FINISHED"}
