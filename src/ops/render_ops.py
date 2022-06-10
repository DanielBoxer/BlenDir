# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator
from ..blendir_main import make_render_folders
from ..utils import get_datetime


class BLENDIR_OT_render_image(Operator):
    bl_idname = "blendir.render_image"
    bl_label = "Render Image"
    bl_description = (
        "Start image render."
        " This will automatically save the image in the output folder"
    )

    def execute(self, context):
        render_path = context.scene.blendir_props.render_path
        if render_path == "":
            default_render_path = bpy.context.scene.render.filepath
            context.scene.blendir_props.render_path = default_render_path
            render_path = default_render_path
        context.scene.render.filepath = render_path + get_datetime(get_time=True)
        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True, use_viewport=True)
        return {"FINISHED"}


class BLENDIR_OT_render_animation(Operator):
    bl_idname = "blendir.render_animation"
    bl_label = "Render Animation"
    bl_description = (
        "Start animation render. If set in the preferences, subfolders will be created "
        "in the output folder. The frames of the animation will be saved there"
    )

    def execute(self, context):
        context.scene.render.filepath = make_render_folders()
        bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
        return {"FINISHED"}
