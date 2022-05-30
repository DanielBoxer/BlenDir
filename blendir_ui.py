# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Panel, Menu
import pathlib


class BLENDIR_PT_main(Panel):
    bl_label = "BlenDir"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenDir"

    def draw(self, context):
        layout = self.layout
        props = context.scene.blendir_props
        box = layout.box()

        row = box.row()
        row.scale_y = 2
        row.operator("blendir.start", icon="NEWFOLDER")

        row = box.row()
        row.scale_y = 2
        row.prop(props, "structure", icon="FILE")

        row = box.box().row()
        row.alignment = "CENTER"
        row.operator("blendir.new_structure", text="", icon="FILE_NEW")
        row.operator("blendir.edit_structure", text="", icon="GREASEPENCIL")
        row.operator("blendir.delete_structure", text="", icon="TRASH")
        row.operator("blendir.import_structure", text="", icon="IMPORT")
        row.operator("blendir.open", text="", icon="FILEBROWSER")


class BLENDIR_PT_input(Panel):
    bl_label = "Input"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenDir"
    bl_parent_id = "BLENDIR_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        props = context.scene.blendir_props

        box = layout.box().column()
        box.label(text="UI Input", icon="TEXT")
        box.prop(props, "x_input", icon="EVENT_X")
        box.prop(props, "y_input", icon="EVENT_Y")
        box.prop(props, "z_input", icon="EVENT_Z")

        layout.separator(factor=0.5)

        box = layout.box().column()
        box.label(text="Date", icon="TIME")
        box.prop(props, "date_format", text="Format")
        box.prop(props, "date_separator", text="Separator")


class BLENDIR_PT_misc(Panel):
    bl_label = "Misc"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenDir"
    bl_parent_id = "BLENDIR_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.blendir_props
        box = layout.box().column()
        box.prop(props, "close_sidebar")
        box.prop(props, "show_create_warning")
        box.prop(props, "show_del_warning")
        row = box.row()
        # enum appears blank if text is not set
        row.prop(props, "open_button", expand=True, text=" ")
        box.operator("blendir.save_settings", icon="FILE_TICK")
        box.operator("blendir.reset_settings", icon="SETTINGS")
        box.operator("blendir.reset", icon="FILE_REFRESH")


class BLENDIR_MT_bookmarks(Menu):
    bl_label = "Bookmarks"

    def draw(self, context):
        pie = self.layout.menu_pie()
        if bpy.data.is_saved:
            bookmarks = context.scene.blendir_bookmarks
            # add all the bookmarks to the pie
            for bookmark_idx, bookmark in enumerate(bookmarks.__annotations__.keys()):
                if bookmarks[bookmark] is not None:
                    pie.operator(
                        "blendir.bookmark",
                        text=pathlib.Path(bookmarks[bookmark]).stem,
                        icon="SOLO_ON",
                    ).bookmark = str(bookmark_idx)
                else:
                    break
