# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Panel, Menu
import pathlib
from .utils import get_preferences, get_references
from .bookmark import get_bookmarks


def draw_prefs(self, context, keymaps):
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
    keymap_item = keymaps[1][1]
    row.prop(keymap_item, "active", text="", full_event=True)
    row.prop(keymap_item, "type", text=keymap_item.name, full_event=True)

    row = box.row()
    keymap_item = keymaps[2][1]
    row.prop(keymap_item, "active", text="", full_event=True)
    row.prop(keymap_item, "type", text=keymap_item.name, full_event=True)

    row = box.row()
    id = "blendir.render_image"
    row.prop(keymap_items[id], "active", text="", full_event=True)
    row.prop(keymap_items[id], "type", text=keymap_items[id].name, full_event=True)

    row = box.row()
    id = "blendir.render_animation"
    row.prop(keymap_items[id], "active", text="", full_event=True)
    row.prop(keymap_items[id], "type", text=keymap_items[id].name, full_event=True)

    box.separator(factor=0)
    row = layout.row()

    col = row.box().column()
    col.label(text="Input", icon="TEXT")
    col.prop(self, "x_input", icon="EVENT_X")
    col.prop(self, "y_input", icon="EVENT_Y")
    col.prop(self, "z_input", icon="EVENT_Z")

    col = row.box().column()

    col.label(text="Date and Time", icon="TIME")
    row = col.row()
    row.alignment = "LEFT"
    row.label(text="Date Format")
    row.prop(self, "date_format")
    row = col.row()
    row.alignment = "LEFT"
    row.label(text="Time Format")
    row.prop(self, "time_format")
    row = col.row()
    row.alignment = "LEFT"
    # the spaces are to align it with the other enums
    row.label(text="Separator     ")
    row.prop(self, "date_separator")

    box.separator(factor=0)
    row = layout.row()

    col = row.box().column()
    col.label(text="Animation Folders", icon="RENDER_ANIMATION")
    col.prop(self, "make_frames_folder")
    col.prop(self, "make_animation_folders")

    col = row.box().column()
    col.label(text="Confirmation", icon="CHECKMARK")
    col.prop(self, "show_create_warning")
    col.prop(self, "show_del_warning")


class BLENDIR_PT_main(Panel):
    bl_label = "BlenDir"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        row = box.row()
        row.scale_y = 2
        row.operator("blendir.start", icon="NEWFOLDER")

        row = box.row()
        row.scale_y = 2
        row.prop(get_preferences(), "structure", icon="FILE")

        row = box.box().row()
        row.alignment = "CENTER"
        row.operator("blendir.new_structure", text="", icon="FILE_NEW")
        row.operator("blendir.edit_structure", text="", icon="GREASEPENCIL")
        row.operator("blendir.delete_structure", text="", icon="TRASH")
        row.operator("blendir.import_structure", text="", icon="IMPORT")

        row = box.box().row()
        row.alignment = "CENTER"
        row.operator("blendir.render_image", text="", icon="RENDER_STILL")
        row.operator("blendir.render_animation", text="", icon="RENDER_ANIMATION")
        row.operator(
            "blendir.directory_browser", text="", icon="BOOKMARKS"
        ).mode = "BOOKMARK"


class BLENDIR_MT_bookmarks(Menu):
    bl_label = "Bookmarks"

    def draw(self, context):
        pie = self.layout.menu_pie()
        # add all saved bookmarks to the pie
        saved_bookmarks = get_bookmarks()
        if saved_bookmarks:
            for bookmark_idx, bookmark in enumerate(saved_bookmarks):
                if bookmark != "":
                    pie.operator(
                        "blendir.bookmark",
                        text=pathlib.Path(bookmark).stem,
                        icon="SOLO_ON",
                    ).bookmark = str(bookmark_idx)

        # add all project bookmarks
        if bpy.data.is_saved:
            bookmark_idx = len(saved_bookmarks)
            bookmarks = context.scene.blendir_bookmarks
            for bookmark in bookmarks.__annotations__.keys():
                if bookmarks[bookmark] is not None and bookmark_idx < 8:
                    pie.operator(
                        "blendir.bookmark",
                        text=pathlib.Path(bookmarks[bookmark]).stem,
                        icon="SOLO_OFF",
                    ).bookmark = str(bookmark_idx)
                    bookmark_idx += 1
                else:
                    break


class BLENDIR_MT_references(Menu):
    bl_label = "References"

    def draw(self, context):
        pie = self.layout.menu_pie()
        for ref_idx, ref in enumerate(get_references()[0]):
            if ref_idx < 8:
                pie.operator(
                    "blendir.reference",
                    text=ref,
                    icon="FUND",
                ).reference = str(ref_idx)
            else:
                break
