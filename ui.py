# BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# END GPL LICENSE BLOCK #####

import bpy
import blf
import bgl

from .operators import *
from .ops_fillarea import *
from .ops_paintbrush import *
from .ops_linebrush import *
from .ops_changeprops import *

class VIEW3D_PT_RopyPanel(bpy.types.Panel):
    """New UI for level editor"""
    bl_label = "Level Editor"
    bl_idname = "VIEW3D_PT_Ropy_Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "Ropy Builder"

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.build_props, "assets_categories")
        row = layout.row()
        row.operator("ropy.link_groups_to_file", icon='LOAD_FACTORY')

        row = layout.row()
        row.prop(scene.build_props, "seed")

        row = layout.row()
        box = row.box()
        box.prop(scene.build_props,"line_scale_factor")
        row = box.row()
        row.prop(scene.build_props, "paint_on_all_objects")
        row = box.row()
        row.operator("ropy.modal_draw_line", text="Line Filled Props", icon='LINE_DATA')

        row = layout.row()
        box = row.box()
        box.prop(scene.build_props, "brush_distance", text="Spacing")
        row = box.row()
        row.prop(scene.build_props, "paint_on_all_objects")
        row = box.row()
        split = row.split(percentage=0.5)
        col = split.column()
        col.prop(scene.build_props, "paint_random_scale")
        if scene.build_props.paint_random_scale:
            col = split.column()
            col.prop(scene.build_props, "paint_random_min_max")

        row = box.row()
        split = row.split(percentage=0.5)
        col = split.column()
        col.prop(scene.build_props, "paint_random_rotation")
        if scene.build_props.paint_random_rotation:
            col = split.column()
            col.prop(scene.build_props, "paint_random_max_angle")


        row = box.row()
        row.operator("ropy.modal_draw_brush",
            text="Draw Props with Brush",
            icon='BRUSH_DATA')

        row = layout.row()
        row.operator("ropy.change_prop_variation")

        row = layout.row()
        box = row.box()
        box.prop(scene.build_props, "props_density", text="Density")
        box.operator("ropy.modal_fill_poly",
            text="Fill Area",
            icon='LINE_DATA')

        row = layout.row()
        box = row.box()
        box.operator("ropy.modal_precise_brush",
            text="Precise Brush",
            icon='LINE_DATA')





class VIEW3D_PT_BuilderEditor_edit_Panel(bpy.types.Panel):
    """UI for level editor in edit mode"""
    bl_label = "Level Editor"
    bl_idname = "VIEW3D_PT_Level_Editor_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "mesh_edit"
    bl_category = "Ropy Builder"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("edit.generate_room", icon='VIEWZOOM')
        row = layout.row()
        row.operator("uv.cube_project", icon='MOD_UVPROJECT')

class PROPERTIES_PT_AssetEditor_database_Panel(bpy.types.Panel):
    """UI for the database management"""
    bl_label = "Database Management"
    bl_idname = "PROPERTIES_PT_asset_editor_database_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        if not context.user_preferences.addons[__package__].preferences.dbPath:
            row.label("Set up the database path in the user preferences")
        else:
            row.operator("ropy.add_cat_to_database")

            row = layout.row()
            row.label('Group Management : ')
            row = layout.row()
            split = row.split(percentage=0.8)
            col = split.column()
            row = col.row()
            row.prop(scene.build_props, "assets_categories")
            row = col.row()
            row.prop(scene.build_props, "current_groups_in_files")

            split = split.split()

            col = split.column()
            row = col.row()
            row = col.row()
            row.scale_y = 2
            row.operator("ropy.add_asset_to_database",icon='FORCE_BOID')

            row = layout.row()
            row.operator("ropy.update_asset_to_database",icon='PLUGIN')

class VIEW3D_PT_RopyExport_Panel(bpy.types.Panel):
    """Export Panel for Ropy Builder"""
    bl_label = "Export Settings"
    bl_idname = "VIEW3D_PT_Ropy_Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "Ropy Builder"

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.build_props, "export_path")

        row = layout.row()
        row.operator("ropy.export_scene", text="Export scene")
