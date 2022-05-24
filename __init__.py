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
    "blender": (2, 80, 0),
    "version": (0, 0, 0),
    "location": "View3D > Sidebar > BlenDir",
    "category": "System",
    "doc_url": "https://github.com/DanielBoxer/BlenDir#readme",
}


import bpy
from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
)
from .blendir_ops import (
    BLENDIR_OT_start,
    BLENDIR_OT_new_structure,
    BLENDIR_OT_edit_structure,
    BLENDIR_OT_delete_structure,
    BLENDIR_OT_open_blend,
    BLENDIR_OT_reset_settings,
    BLENDIR_OT_reset,
)
from .blendir_ui import (
    BLENDIR_PT_main,
    BLENDIR_PT_input,
    BLENDIR_PT_misc,
)
from .blendir_main import init_structs, update_structs


class BLENDIR_PG_properties(bpy.types.PropertyGroup):
    # non UI properties
    old_path: StringProperty()
    struct_items = init_structs()[0]
    struct_icon: StringProperty(default=init_structs()[1])

    # input properties
    structure: EnumProperty(name="", description="Structure", items=update_structs)
    x_input: StringProperty(
        name="",
        description="If a line has '*X', it will be replaced with this field",
    )
    y_input: StringProperty(
        name="",
        description="If a line has '*Y', it will be replaced with this field",
    )
    z_input: StringProperty(
        name="",
        description="If a line has '*Z', it will be replaced with this field",
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
        name="", description="Show an extra warning before deleting files", default=True
    )
    show_create_warning: BoolProperty(
        name="",
        description="Show a warning before creating folders after the first time",
        default=True,
    )


classes = (
    BLENDIR_OT_start,
    BLENDIR_OT_new_structure,
    BLENDIR_OT_edit_structure,
    BLENDIR_OT_delete_structure,
    BLENDIR_OT_open_blend,
    BLENDIR_OT_reset_settings,
    BLENDIR_OT_reset,
    BLENDIR_PT_main,
    BLENDIR_PT_input,
    BLENDIR_PT_misc,
    BLENDIR_PG_properties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.blendir_props = bpy.props.PointerProperty(
        type=BLENDIR_PG_properties
    )


def unregister():
    del bpy.types.Scene.blendir_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
