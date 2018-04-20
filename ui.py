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

def draw_typo_2d(color,x,y, text):
    font_id = 0
    bgl.glColor4f(*color)
    blf.position(font_id, x, y, 0)
    blf.size(font_id, 12, 72)
    blf.draw(font_id, text)


def draw_callback_change_prop_px(self,context):
    region = context.region
    rv3d = context.space_data.region_3d

    bgl.glEnable(bgl.GL_BLEND)
    draw_typo_2d((1.0,1.0,1.0,1),100,100,"cocuou")
    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)


def draw_callback_brush_px(self, context):
    region = context.region
    rv3d = context.space_data.region_3d

    if self.surface_found: #if there is a surface under mouse cursor
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(1.0, 1.0, 0.0, 1.0)
        bgl.glLineWidth(1)
        bgl.glEnable(bgl.GL_LINE)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.surface_normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)
        bgl.glDisable(bgl.GL_BLEND)


def draw_callback_line_px(self, context):
    region = context.region
    rv3d = context.space_data.region_3d

    # Draw Points
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.8, 0.0, 1.0)
    bgl.glPointSize(5.0)
    bgl.glBegin(bgl.GL_POINTS)
    # bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

    for x in self.list_construction_points:
        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point)
        bgl.glVertex2f(loc_1[0], loc_1[1])

    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)

    # Draw Normal point
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.3, 0.8, 0.8, 1.0)
    bgl.glPointSize(2.0)
    bgl.glBegin(bgl.GL_POINTS)

    for x in self.list_construction_points:
        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point+x.normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])

    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)

    # 50% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 0.0, 0.0, 1.0)
    bgl.glLineStipple(2, 0x9999)
    bgl.glEnable(bgl.GL_LINE)
    bgl.glBegin(bgl.GL_LINE_STRIP)

    for x in self.list_construction_points:
        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point)
        bgl.glVertex2f(loc_1[0], loc_1[1])
    bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])
    bgl.glEnd()
    bgl.glDisable(bgl.GL_LINE_STRIP)
    bgl.glDisable(bgl.GL_BLEND)


    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1.0, 1.0, 0.0, 1.0)
    bgl.glLineWidth(1)
    for x in self.list_construction_points:
        bgl.glEnable(bgl.GL_LINE)
        bgl.glBegin(bgl.GL_LINE_STRIP)

        root = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point)
        bgl.glVertex2f(root[0], root[1])
        tip = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point+x.normal)
        bgl.glVertex2f(tip[0], tip[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)
    bgl.glDisable(bgl.GL_BLEND)

    if self.surface_found: #if there is a surface under mouse cursor
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(1.0, 1.0, 0.0, 1.0)
        bgl.glLineWidth(1)
        bgl.glEnable(bgl.GL_LINE)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

        loc_1 = bpy_extras.view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.surface_normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)
        bgl.glDisable(bgl.GL_BLEND)


    # restore opengl defaults
    # bgl.glLineWidth(1)
    # bgl.glDisable(bgl.GL_BLEND)
    # bgl.glColor4f(0.0, 0.0, 0.0, 1.0)

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
        row.operator("ropy.modal_draw_brush", text="Draw Props with Brush", icon='BRUSH_DATA')

        row = layout.row()
        row.operator("ropy.change_prop_variation")

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
