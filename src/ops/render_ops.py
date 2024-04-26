# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

import bpy
from bpy.types import Operator

from ..blendir_main import make_render_folders
from ..utils import get_datetime


def add_camera(context):
    # check for camera
    if any(obj.type == "CAMERA" for obj in context.scene.objects):
        return False

    # if no camera found, add camera to current view
    camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    context.collection.objects.link(camera)
    context.scene.camera = camera

    v3d = None
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            v3d = area
            break

    if v3d is not None:
        camera.matrix_world = v3d.spaces[0].region_3d.view_matrix.inverted()

    return True


class BLENDIR_OT_render_image(Operator):
    bl_idname = "blendir.render_image"
    bl_label = "Render Image"
    bl_description = (
        "Start image render."
        " This will automatically save the image in the output folder"
    )

    def execute(self, context):
        scene = context.scene
        add_camera(context)

        render_path = scene.blendir_props.render_path
        if render_path == "":
            default_render_path = scene.render.filepath
            scene.blendir_props.render_path = default_render_path
            render_path = default_render_path
        scene.render.filepath = render_path + get_datetime(get_time=True)
        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True, use_viewport=True)

        self.report({"INFO"}, f"Image saved to {scene.render.filepath}")
        return {"FINISHED"}


class BLENDIR_OT_render_animation(Operator):
    bl_idname = "blendir.render_animation"
    bl_label = "Render Animation"
    bl_description = (
        "Start animation render. If set in the preferences, subfolders will be created "
        "in the output folder. The frames of the animation will be saved there"
    )

    def execute(self, context):
        add_camera(context)
        context.scene.render.filepath = make_render_folders()
        bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
        self.report({"INFO"}, f"Animation saved to {context.scene.render.filepath}")
        return {"FINISHED"}
