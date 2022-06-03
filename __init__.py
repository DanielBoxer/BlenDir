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
    "version": (0, 17, 1),
    "location": "View3D > Sidebar > BlenDir",
    "category": "System",
    "doc_url": "https://github.com/DanielBoxer/BlenDir#readme",
    "tracker_url": "https://github.com/DanielBoxer/BlenDir/issues",
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
    BLENDIR_OT_save_default,
    BLENDIR_OT_bookmark,
    BLENDIR_OT_edit_bookmarks,
    BLENDIR_OT_reference,
)
from .blendir_ui import (
    BLENDIR_PT_main,
    BLENDIR_MT_bookmarks,
    BLENDIR_MT_references,
    draw_prefs,
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
    reference_path: StringProperty()

    structure: EnumProperty(
        name="",
        description="Structure",
        items=update_structs,
        # load startup data
        default=load_startup()["structure"],
    )
    struct_name: StringProperty(
        name="Structure Name",
        description="Enter the name of the structure",
    )


class BLENDIR_PG_bookmarks(bpy.types.PropertyGroup):
    b0: StringProperty()
    b1: StringProperty()
    b2: StringProperty()
    b3: StringProperty()
    b4: StringProperty()
    b5: StringProperty()
    b6: StringProperty()
    b7: StringProperty()


class BLENDIR_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = pathlib.Path(__file__).resolve().parent.stem

    # the previous save location
    last_path: StringProperty()

    # input properties
    x_input: StringProperty(
        name="", description="If a line has '*X', it will be replaced with this field"
    )
    y_input: StringProperty(
        name="", description="If a line has '*Y', it will be replaced with this field"
    )
    z_input: StringProperty(
        name="", description="If a line has '*Z', it will be replaced with this field"
    )
    date_format: EnumProperty(
        name="",
        description="If a line has '*D', it will be replaced with the current date",
        items=[
            ("YMD", "YYYY/MM/DD", ""),
            ("MDY", "MM/DD/YYYY", ""),
            ("DMY", "DD/MM/YYYY", ""),
        ],
    )
    date_separator: EnumProperty(
        name="",
        description="The character used to separate the year, month and day",
        items=[
            ("-", "Dash", ""),
            ("_", "Underscore", ""),
            (" ", "None", ""),
        ],
    )

    # misc properties
    show_del_warning: BoolProperty(
        name="Confirm File Deletion",
        description="Show an extra warning before deleting files",
        default=True,
    )
    show_create_warning: BoolProperty(
        name="Confirm Folder Creation",
        description="Show a warning before creating folders after the first time",
        default=True,
    )

    def draw(self, context):
        draw_prefs(self, context, keymaps)


keymaps = []
classes = (
    BLENDIR_OT_start,
    BLENDIR_OT_new_structure,
    BLENDIR_OT_edit_structure,
    BLENDIR_OT_delete_structure,
    BLENDIR_OT_import_structure,
    BLENDIR_OT_directory_browser,
    BLENDIR_OT_save_blend,
    BLENDIR_OT_save_default,
    BLENDIR_OT_bookmark,
    BLENDIR_OT_edit_bookmarks,
    BLENDIR_OT_reference,
    BLENDIR_PT_main,
    BLENDIR_MT_bookmarks,
    BLENDIR_MT_references,
    BLENDIR_PG_properties,
    BLENDIR_PG_bookmarks,
    BLENDIR_AP_preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blendir_props = bpy.props.PointerProperty(
        type=BLENDIR_PG_properties
    )
    bpy.types.Scene.blendir_bookmarks = bpy.props.PointerProperty(
        type=BLENDIR_PG_bookmarks
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

        id = "wm.call_menu_pie"
        keymap_item = keymap.keymap_items.new(id, type="F", value="PRESS", shift=True)
        keymap_item.properties.name = "BLENDIR_MT_bookmarks"
        keymaps.append((keymap, keymap_item))

        keymap_item = keymap.keymap_items.new(id, type="F", value="PRESS", ctrl=True)
        keymap_item.properties.name = "BLENDIR_MT_references"
        keymaps.append((keymap, keymap_item))


def unregister():
    # remove keymaps
    for keymap, keymap_item in keymaps:
        keymap.keymap_items.remove(keymap_item)
    keymaps.clear()

    del bpy.types.Scene.blendir_bookmarks
    del bpy.types.Scene.blendir_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
