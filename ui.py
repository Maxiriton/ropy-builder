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

class VIEW3D_PT_BuilderEditorPanel(bpy.types.Panel):
    """UI for level editor"""
    bl_label = "Level Editor"
    bl_idname = "VIEW3D_PT_Level_Editor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "Artemis"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.prop(scene.builder_editor, "seed")


        row = layout.row()
        row.operator("view3d.modal_draw_line", text="Line Filled Props", icon='LINE_DATA')
        row = layout.row()
        row.prop(scene.builder_editor, "brush_distance")
        row = layout.row()
        row.operator("view3d.modal_draw_brush", text="Draw Props with Brush", icon='BRUSH_DATA')


class VIEW3D_PT_BuilderEditor_edit_Panel(bpy.types.Panel):
    """UI for level editor in edit mode"""
    bl_label = "Level Editor"
    bl_idname = "VIEW3D_PT_Level_Editor_edit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "mesh_edit"
    bl_category = "Artemis"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.operator("edit.generate_room", icon='VIEWZOOM')
        row = layout.row()
        row.operator("uv.cube_project", icon='MOD_UVPROJECT')
