# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from ..blendir_main import BlenDirError
from ..utils import open_path
from ..bookmark import get_bookmarks, open_bookmarks


class BLENDIR_OT_bookmark(Operator):
    bl_idname = "blendir.bookmark"
    bl_label = "Bookmark"
    bl_description = "Bookmark"

    bookmark: bpy.props.EnumProperty(
        items=(
            ("0", "0", ""),
            ("1", "1", ""),
            ("2", "2", ""),
            ("3", "3", ""),
            ("4", "4", ""),
            ("5", "5", ""),
            ("6", "6", ""),
            ("7", "7", ""),
        )
    )

    def execute(self, context):
        selected = int(self.bookmark)
        saved_bookmarks = get_bookmarks()
        if len(saved_bookmarks) > selected:
            open_path(saved_bookmarks[selected], True)
        else:
            bookmarks = context.scene.blendir_bookmarks
            bookmark_idx = len(saved_bookmarks)
            for bookmark in bookmarks.__annotations__.keys():
                if bookmark_idx == selected:
                    open_path(bookmarks[bookmark], True)
                    break
                bookmark_idx += 1
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
