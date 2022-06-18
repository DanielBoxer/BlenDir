# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty
from ..blendir_main import BlenDirError
from ..utils import open_path
from ..bookmark import get_bookmarks, open_bookmarks


_co = [0, 0]


class BLENDIR_OT_bookmarks(Operator):
    bl_idname = "blendir.bookmarks"
    bl_label = "Bookmarks"
    bl_description = "Bookmarks"

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        box = layout.box()
        box.label(text="Bookmarks", icon="BOOKMARKS")
        box.separator(factor=0)

        col = box.box().column()
        col.label(text="Press 'Open Directory Browser' to add bookmarks.")
        col.label(text="Press 'Edit Bookmarks' to change / delete bookmarks.")
        col.separator(factor=2)

        row = col.row()
        row.scale_y = 2
        row.operator_context = "INVOKE_DEFAULT"
        row.operator(
            "blendir.directory_browser",
            text="Open Directory Browser",
            icon="FILEBROWSER",
        ).mode = "BOOKMARK"

        row = col.row()
        row.scale_y = 2
        row.operator("blendir.edit_bookmarks", icon="GREASEPENCIL")


class BLENDIR_OT_open_bookmark(Operator):
    bl_idname = "blendir.open_bookmark"
    bl_label = "Bookmark"
    bl_description = "Bookmark"

    bookmark_idx: IntProperty()

    def execute(self, context):
        bookmarks = []
        for bookmark in context.scene.blendir_bookmarks:
            bookmarks.append(bookmark.path)
        bookmarks += get_bookmarks()
        open_path(bookmarks[self.bookmark_idx], True)
        return {"FINISHED"}


class BLENDIR_OT_edit_bookmarks(Operator):
    bl_idname = "blendir.edit_bookmarks"
    bl_label = "Edit Bookmarks"
    bl_description = "Edit bookmarks"

    def execute(self, context):
        try:
            open_bookmarks()
        except BlenDirError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        return {"FINISHED"}


class BLENDIR_OT_change_page(Operator):
    bl_idname = "blendir.change_page"
    bl_label = "Page"
    bl_description = "Change Page"

    mode: EnumProperty(
        items=[
            ("NEXT", "0", ""),
            ("PREVIOUS", "1", ""),
        ],
    )

    def execute(self, context):
        props = context.scene.blendir_props
        if self.mode == "NEXT":
            props.bookmark_page += 1
        else:
            props.bookmark_page -= 1

        # set mouse position to the position when the menu was opened
        # this keeps the menu in the same position when changing pages
        context.window.cursor_warp(_co[0], _co[1])

        bpy.ops.wm.call_menu_pie("INVOKE_DEFAULT", name="BLENDIR_MT_bookmarks_pie")
        return {"FINISHED"}


class BLENDIR_OT_open_bookmarks_pie(Operator):
    bl_idname = "blendir.open_bookmarks_pie"
    bl_label = "Open Bookmarks Pie"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie("INVOKE_DEFAULT", name="BLENDIR_MT_bookmarks_pie")
        return {"FINISHED"}

    def invoke(self, context, event):
        _co[0] = event.mouse_x
        _co[1] = event.mouse_y
        return self.execute(context)
