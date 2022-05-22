# Copyright (C) 2022 Daniel Boxer
# See __init__.py and LICENSE for more information

from bpy.types import Panel


class BLENDIR_PT_main(Panel):
    bl_label = "BlenDir"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenDir"

    def draw(self, context):
        layout = self.layout
        props = context.scene.blendir_props

        box = layout.box()
        box.scale_y = 2
        box.operator("blendir.start", icon="NEWFOLDER")
        box.prop(props, "structure", icon="FILE")


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
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box().column()
        box.operator("blendir.reset_settings", icon="SETTINGS")
        box.operator("blendir.reset", icon="FILE_REFRESH")
