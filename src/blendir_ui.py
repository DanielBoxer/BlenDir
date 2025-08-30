# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import pathlib

import bpy
from bpy.types import Menu, Panel

from .bookmark import get_bookmarks
from .recent import get_recent
from .utils import (
    get_panel_category,
    get_preferences,
    get_references,
)


def draw_prefs(self, context, keymaps):
    layout = self.layout

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

    row = layout.row()

    col = row.box().column()
    col.label(text="Animation Folders", icon="RENDER_ANIMATION")
    col.prop(self, "make_frames_folder")
    col.prop(self, "make_animation_folders")

    col = row.box().column()
    col.label(text="Confirmation", icon="CHECKMARK")
    col.prop(self, "show_create_warning")
    col.prop(self, "show_del_warning")

    col = row.box().column()
    col.label(text="Recent Projects", icon="FILE_BLEND")
    col.prop(self, "autoload_refs")
    col.operator("blendir.edit_recent")

    box = layout.box()

    row = box.row()
    row.alignment = "CENTER"
    row.label(text="Keymap", icon="EVENT_OS")

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
    id = "blendir.open_bookmarks_pie"
    row.prop(keymap_items[id], "active", text="", full_event=True)
    row.prop(keymap_items[id], "type", text=keymap_items[id].name, full_event=True)
    row = box.row()
    keymap_item = keymaps[2][1]
    row.prop(keymap_item, "active", text="", full_event=True)
    row.prop(keymap_item, "type", text=keymap_item.name, full_event=True)
    row = box.row()
    keymap_item = keymaps[3][1]
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

    box = layout.box()

    row = box.row()
    row.alignment = "CENTER"
    row.label(text="Misc", icon="SETTINGS")

    box.prop(self, "verbose_ui")

    split = box.split(factor=0.8)
    split.prop(self, "panel_category")
    split.operator("blendir.save_panel_category")

    box.operator("blendir.export")
    box.operator("blendir.import")

    props = context.scene.blendir_props
    # iterate over all props in property group
    if any(getattr(props, key) for key in props.__annotations__.keys()):
        # show reset op if there are any saved props
        box.operator("blendir.reset_props")


class BLENDIR_PT_main(Panel):
    bl_label = "BlenDir"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = get_panel_category()

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        prefs = get_preferences()

        row = box.row()
        row.scale_y = 2
        row.operator("blendir.start", icon="NEWFOLDER")

        row = box.row()
        row.scale_y = 2
        row.prop(prefs, "structure", icon="FILE")

        button_groups = (
            (
                ("new_structure", "New Structure", "FILE_NEW"),
                ("edit_structure", "Edit Structure", "GREASEPENCIL"),
                ("delete_structure", "Delete Structure", "TRASH"),
                ("import_structure", "Import Structure", "IMPORT"),
            ),
            (
                ("render_image", "Render Image", "RENDER_STILL"),
                ("render_animation", "Render Animation", "RENDER_ANIMATION"),
                ("bookmarks", "Edit Bookmarks", "BOOKMARKS"),
                ("open_preferences", "Preferences", "PREFERENCES"),
            ),
        )

        if not prefs.verbose_ui:
            for group in button_groups:
                row = box.box().row()
                row.alignment = "CENTER"
                for operator, _, icon in group:
                    row.operator(f"blendir.{operator}", text="", icon=icon)
        else:
            for group in button_groups:
                col = box.box().column()
                col.alignment = "CENTER"
                for operator, text, icon in group:
                    row = col.row()
                    row.scale_y = 1.25
                    row.operator(f"blendir.{operator}", text=text, icon=icon)


class BLENDIR_MT_bookmarks_pie(Menu):
    bl_label = "Bookmarks"

    def draw(self, context):
        page = context.scene.blendir_props.bookmark_page
        pie = self.layout.menu_pie()
        bookmark_list = {}
        # add all project bookmarks
        if bpy.data.is_saved:
            bookmarks = context.scene.blendir_bookmarks
            for bookmark in bookmarks:
                bookmark_list[bookmark.path] = "SOLO_OFF"
        # add all saved bookmarks
        for bookmark in get_bookmarks():
            if bookmark != "":
                bookmark_list[bookmark] = "SOLO_ON"

        bookmark_count = len(bookmark_list)
        low_idx = page * 8 - page
        high_idx = low_idx + 8
        iter_bookmarks = enumerate(list(bookmark_list.keys())[low_idx:], low_idx)
        for bookmark_idx, bookmark in iter_bookmarks:
            if bookmark_idx == high_idx:
                # pie menu can only have 8 items
                break
            if bookmark_idx == low_idx and bookmark_count > 8:
                box = pie.box()
                row = box.row()
                row.alignment = "CENTER"
                row.label(text=f"Page {page + 1}", icon="BOOKMARKS")
                if bookmark_count - high_idx >= 0:
                    next_op = box.operator(
                        "blendir.change_page",
                        text="Next",
                        icon="TRIA_RIGHT",
                    )
                    next_op.mode = "NEXT"

                if page > 0:
                    previous_op = box.operator(
                        "blendir.change_page",
                        text="Previous",
                        icon="TRIA_LEFT",
                    )
                    previous_op.mode = "PREVIOUS"

                # subtract 1 because two items will be drawn on this iteration
                high_idx -= 1

            pie.operator(
                "blendir.open_bookmark",
                text=pathlib.Path(bookmark).stem,
                icon=bookmark_list[bookmark],
            ).bookmark_idx = bookmark_idx


class BLENDIR_MT_references_pie(Menu):
    bl_label = "References"

    def draw(self, context):
        pie = self.layout.menu_pie()
        for ref_idx, ref in enumerate(get_references()[0]):
            if ref_idx < 8:
                pie.operator(
                    "blendir.open_reference",
                    text=ref,
                    icon="IMAGE_REFERENCE",
                ).reference_idx = ref_idx
            else:
                break


class BLENDIR_MT_recent_pie(Menu):
    bl_label = "Recent"

    def draw(self, context):
        pie = self.layout.menu_pie()
        for path_idx, path in enumerate(get_recent()):
            pie.operator(
                "blendir.open_recent",
                text=pathlib.Path(path).stem,
                icon="BLENDER",
            ).recent_idx = path_idx
