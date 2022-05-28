# Copyright (C) 2022 Daniel Boxer
#
# BlenDir is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# BlenDir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenDir. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "BlenDir",
    "author": "Daniel Boxer",
    "description": "Automatic folder structure",
    "blender": (2, 90, 0),
    "version": (0, 12, 1),
    "location": "View3D > Sidebar > BlenDir",
    "category": "System",
    "doc_url": "https://github.com/DanielBoxer/BlenDir#readme",
    "tracker_url": "https://github.com/DanielBoxer/BlenDir/issues",
    "warning": "Work in Progress",
}


import bpy
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
)
import pathlib
from .blendir_ops import (
    BLENDIR_OT_start,
    BLENDIR_OT_new_structure,
    BLENDIR_OT_edit_structure,
    BLENDIR_OT_delete_structure,
    BLENDIR_OT_import_structure,
    BLENDIR_OT_directory_browser,
    BLENDIR_OT_save_blend,
    BLENDIR_OT_open,
    BLENDIR_OT_save_settings,
    BLENDIR_OT_reset_settings,
    BLENDIR_OT_reset,
)
from .blendir_ui import (
    BLENDIR_PT_main,
    BLENDIR_PT_input,
    BLENDIR_PT_misc,
)
from .blendir_main import (
    init_structs,
    update_structs,
    load_startup,
)


class BLENDIR_PG_properties(bpy.types.PropertyGroup):
    # non UI properties
    old_path: StringProperty()
    struct_items = init_structs()[0]
    struct_icon: StringProperty(default=init_structs()[1])

    # load startup data
    startup_data = load_startup()

    # input properties
    structure: EnumProperty(
        name="",
        description="Structure",
        items=update_structs,
        default=startup_data["structure"],
    )
    x_input: StringProperty(
        name="",
        description="If a line has '*X', it will be replaced with this field",
        default=startup_data["x_input"],
    )
    y_input: StringProperty(
        name="",
        description="If a line has '*Y', it will be replaced with this field",
        default=startup_data["y_input"],
    )
    z_input: StringProperty(
        name="",
        description="If a line has '*Z', it will be replaced with this field",
        default=startup_data["z_input"],
    )
    date_format: EnumProperty(
        name="",
        description="If a line has '*D', it will be replaced with the current date",
        items=[
            ("YMD", "YYYY/MM/DD", ""),
            ("MDY", "MM/DD/YYYY", ""),
            ("DMY", "DD/MM/YYYY", ""),
        ],
        default=startup_data["date_format"],
    )
    date_separator: EnumProperty(
        name="",
        description="The character used to separate the year, month and day",
        items=[
            ("-", "Dash", ""),
            ("_", "Underscore", ""),
            (" ", "None", ""),
        ],
        default=startup_data["date_separator"],
    )

    # misc properties
    show_del_warning: BoolProperty(
        name="Confirm File Deletion",
        description="Show an extra warning before deleting files",
        default=startup_data["show_del_warning"],
    )
    show_create_warning: BoolProperty(
        name="Confirm Folder Creation",
        description="Show a warning before creating folders after the first time",
        default=startup_data["show_create_warning"],
    )
    struct_name: StringProperty(
        name="Structure Name",
        description="Enter the name of the structure",
    )
    close_sidebar: BoolProperty(
        name="Auto Close Sidebar",
        description=(
            "Automatically close the sidebar after 'Create Folders' button is pressed"
        ),
        default=startup_data["close_sidebar"],
    )
    open_button: EnumProperty(
        name="",
        description="Behaviour of the 'Open' button",
        items=[
            (
                "BLEND",
                "Blend",
                "Open the folder where the current blender file is saved",
            ),
            (
                "PROJECT",
                "Project",
                "Open the project folder",
            ),
            (
                "ROOT",
                "Root",
                "Open the folder above the project folder",
            ),
        ],
        default=startup_data["open_button"],
    )


class BLENDIR_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = pathlib.Path(__file__).resolve().parent.stem

    # the previous save location
    last_path: bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label(text="Keymap", icon="EVENT_OS")
        box.separator()

        user_keymaps = context.window_manager.keyconfigs.user.keymaps["3D View"]
        keymap_items = user_keymaps.keymap_items
        # update the stored keymap
        layout.context_pointer_set("keymap", user_keymaps)

        row = box.row()
        id = "blendir.start"
        # keymap activation checkbox
        row.prop(keymap_items[id], "active", text="", full_event=True)
        # keymap input button
        row.prop(keymap_items[id], "type", text=keymap_items[id].name, full_event=True)

        row = box.row()
        id = "blendir.open"
        row.prop(keymap_items[id], "active", text="", full_event=True)
        row.prop(keymap_items[id], "type", text=keymap_items[id].name, full_event=True)
        box.separator(factor=0)


keymaps = []
classes = (
    BLENDIR_OT_start,
    BLENDIR_OT_new_structure,
    BLENDIR_OT_edit_structure,
    BLENDIR_OT_delete_structure,
    BLENDIR_OT_import_structure,
    BLENDIR_OT_directory_browser,
    BLENDIR_OT_save_blend,
    BLENDIR_OT_open,
    BLENDIR_OT_save_settings,
    BLENDIR_OT_reset_settings,
    BLENDIR_OT_reset,
    BLENDIR_PT_main,
    BLENDIR_PT_input,
    BLENDIR_PT_misc,
    BLENDIR_PG_properties,
    BLENDIR_AP_preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blendir_props = bpy.props.PointerProperty(
        type=BLENDIR_PG_properties
    )

    # add keymaps
    key_config = bpy.context.window_manager.keyconfigs.addon
    if key_config:
        keymap = key_config.keymaps.new("3D View", space_type="VIEW_3D")
        id = "blendir.start"
        keymap_item = keymap.keymap_items.new(
            id, type="F", value="PRESS", shift=True, ctrl=True
        )
        keymaps.append((keymap, keymap_item))

        keymap = key_config.keymaps.new("3D View", space_type="VIEW_3D")
        id = "blendir.open"
        keymap_item = keymap.keymap_items.new(id, type="F", value="PRESS", shift=True)
        keymaps.append((keymap, keymap_item))


def unregister():
    # remove keymaps
    for keymap, keymap_item in keymaps:
        keymap.keymap_items.remove(keymap_item)
    keymaps.clear()

    del bpy.types.Scene.blendir_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
