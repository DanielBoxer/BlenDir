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
    "version": (0, 18, 3),
    "location": (
        "View3D > Sidebar > Tool & Properties > Active Tool and Workspace settings"
    ),
    "category": "System",
    "doc_url": "https://github.com/DanielBoxer/BlenDir#readme",
    "tracker_url": "https://github.com/DanielBoxer/BlenDir/issues",
}


import bpy
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
)
import pathlib
from .src.ops.blendir_ops import (
    BLENDIR_OT_start,
    BLENDIR_OT_directory_browser,
    BLENDIR_OT_save_blend,
    BLENDIR_OT_reference,
)
from .src.ops.structure_ops import (
    BLENDIR_OT_new_structure,
    BLENDIR_OT_edit_structure,
    BLENDIR_OT_delete_structure,
    BLENDIR_OT_import_structure,
)
from .src.ops.bookmark_ops import (
    BLENDIR_OT_bookmarks,
    BLENDIR_OT_open_bookmark,
    BLENDIR_OT_edit_bookmarks,
    BLENDIR_OT_change_page,
    BLENDIR_OT_open_bookmarks_pie,
)
from .src.ops.render_ops import (
    BLENDIR_OT_render_animation,
    BLENDIR_OT_render_image,
)
from .src.blendir_ui import (
    BLENDIR_PT_main,
    BLENDIR_MT_bookmarks_pie,
    BLENDIR_MT_references,
    draw_prefs,
)
from .src.structure import init_structs, update_structs
from .src.bookmark import BLENDIR_PG_bookmark


class BLENDIR_PG_properties(bpy.types.PropertyGroup):
    # non UI properties
    old_path: StringProperty()
    reference_path: StringProperty()
    render_path: StringProperty()
    bookmark_page: IntProperty()


class BLENDIR_AP_preferences(bpy.types.AddonPreferences):
    bl_idname = pathlib.Path(__file__).parent.stem

    struct_data = init_structs()
    struct_items = struct_data[0]
    struct_icon = struct_data[1]
    structure: EnumProperty(name="", description="Structure", items=update_structs)

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
    # date time properties
    date_format: EnumProperty(
        name="",
        description="If a line has '*D', it will be replaced with the current date",
        items=[
            ("YMD", "YYYY/MM/DD", ""),
            ("MDY", "MM/DD/YYYY", ""),
            ("DMY", "DD/MM/YYYY", ""),
        ],
    )
    time_format: EnumProperty(
        name="",
        description="Time format for image renders",
        items=[
            ("HMS", "HH/MM/SS", ""),
            ("MS", "MM/SS", ""),
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
    # animation folders properties
    make_frames_folder: BoolProperty(
        name="Make Folder for Frames",
        description=(
            "Make a subfolder in the render folder to hold all the animation folders"
        ),
        default=True,
    )
    make_animation_folders: BoolProperty(
        name="Make Animation Folders",
        description=(
            "Make a new folder for each animation render and save the frames there"
        ),
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
    BLENDIR_OT_bookmarks,
    BLENDIR_OT_open_bookmark,
    BLENDIR_OT_edit_bookmarks,
    BLENDIR_OT_change_page,
    BLENDIR_OT_open_bookmarks_pie,
    BLENDIR_OT_reference,
    BLENDIR_OT_render_animation,
    BLENDIR_OT_render_image,
    BLENDIR_PT_main,
    BLENDIR_MT_bookmarks_pie,
    BLENDIR_MT_references,
    BLENDIR_PG_properties,
    BLENDIR_PG_bookmark,
    BLENDIR_AP_preferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blendir_props = bpy.props.PointerProperty(
        type=BLENDIR_PG_properties
    )
    bpy.types.Scene.blendir_bookmarks = bpy.props.CollectionProperty(
        type=BLENDIR_PG_bookmark
    )

    # add keymaps
    key_config = bpy.context.window_manager.keyconfigs.addon
    if key_config:
        keymap = key_config.keymaps.new("3D View", space_type="VIEW_3D")

        keymap_item = keymap.keymap_items.new(
            "blendir.start", type="F", value="PRESS", shift=True, ctrl=True
        )
        keymaps.append((keymap, keymap_item))

        keymap_item = keymap.keymap_items.new(
            "blendir.open_bookmarks_pie", type="F", value="PRESS", shift=True
        )
        keymaps.append((keymap, keymap_item))

        id = "wm.call_menu_pie"
        keymap_item = keymap.keymap_items.new(id, type="F", value="PRESS", ctrl=True)
        keymap_item.properties.name = "BLENDIR_MT_references"
        keymaps.append((keymap, keymap_item))

        keymap_item = keymap.keymap_items.new(
            "blendir.render_image", type="F12", value="PRESS", shift=True
        )
        keymaps.append((keymap, keymap_item))

        keymap_item = keymap.keymap_items.new(
            "blendir.render_animation", type="F12", value="PRESS", shift=True, ctrl=True
        )
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
