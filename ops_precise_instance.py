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


import mathutils

from .functions import *
from .database import *
from .draw import draw_callback_precise_brush

class ModalPreciseBrushOperator(bpy.types.Operator):
    """Draw props on scene"""
    bl_idname = "ropy.modal_precise_brush"
    bl_label = "Precision Brush"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    current_var = 0
    group_list = []
    temp_obj = []



    def add_prop(self,context,location,rotation):
        group_name = self.group_list[self.current_var][1]
        e = add_prop_instance(context,group_name)

        loc_mat = Matrix.Translation(location)

        scale_mat = Matrix.Scale(1,4,(1,0,0))*Matrix.Scale(1,4,(0,1,0)) * Matrix.Scale(1,4,(0,0,1))

        v0 = Vector(( 0.0,0,1.0 ))
        orig_rot_mat = v0.rotation_difference(rotation).to_matrix().to_4x4()

        mat_rot =  mathutils.Matrix.Rotation(0, 4, rotation)
        e.matrix_world = loc_mat * mat_rot * orig_rot_mat * scale_mat

        self.temp_obj.append(e)
        #we need to update the index for next addition
        self.current_var = (self.current_var+1) % len(self.group_list)


    def modal(self,context,event):
        context.area.tag_redraw()
        region = context.region
        rv3d = context.space_data.region_3d

        if event.type == 'MOUSEMOVE':
            coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            self.mouse_path = coord_mouse

            # get the ray from the viewport and mouse
            best_hit,best_obj,best_normal,best_face_index =get_ray_cast_result(
                                    context,
                                    coord_mouse,
                                    context.scene.build_props.paint_on_all_objects)

            self.surface_found = False
            if best_hit is not None:
                self.surface_found = True
                self.surface_normal = best_hit + best_normal
                self.surface_hit = best_hit

                if self.lmb: #if the left button is pressed
                    self.delta = (self.previous_impact - self.surface_hit).length
                    self.help_string = str(self.delta)
                    context.area.header_text_set(self.help_string)

                    e = self.temp_obj[-1]

                    loc_mat = Matrix.Translation(e.location)

                    scale_mat = Matrix.Scale(1,4,(1,0,0)) * Matrix.Scale(1,4,(0,1,0)) * Matrix.Scale(1,4,(0,0,1))
                    factor = self.delta*0.3
                    scale_mat = Matrix.Scale(factor,4,(1,0,0)) * Matrix.Scale(factor,4,(0,1,0)) * Matrix.Scale(factor,4,(0,0,1))

                    # v0 = Vector(( 0.0,0,1.0 ))
                    # orig_rot_mat = v0.rotation_difference(e.rotation_euler).to_matrix().to_4x4()

                    mat_rot =  mathutils.Matrix.Rotation(0, 4, e.rotation_euler)

                    # factor = 1
                    # mat_rot = mathutils.Matrix.Rotation(factor, 4, e.rotation_euler)

                    e.matrix_world = loc_mat * mat_rot * scale_mat

                    self.help_string = str(mat_rot)
                    context.area.header_text_set(self.help_string)




        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.lmb = True
                coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
                # get the ray from the viewport and mouse
                best_hit,best_obj,best_normal,best_face_index = get_ray_cast_result(context,coord_mouse,context.scene.build_props.paint_on_all_objects)
                if best_hit is not None:
                    self.previous_impact = best_hit
                    self.delta = 0
                    self.add_prop(context,best_hit,best_normal)

            elif event.value == 'RELEASE':
                self.lmb = False

        elif event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                try:
                    last_obj = self.temp_obj[-1]
                    self.temp_obj.pop()
                    delete_temp_objects(context,[last_obj.name])
                except:
                    print('List is Empty !')

        elif event.type  in {'S'} and event.value == 'PRESS':
            context.scene.build_props.brush_distance +=  0.1
        elif event.type in {'R'} and event.value == 'PRESS':
            context.scene.build_props.brush_distance +=  -0.1
        elif event.type in {'ESC','RET'}:
            context.area.header_text_set()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.depth_location = Vector((0.0, 0.0, 0.0))
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_precise_brush, args, 'WINDOW', 'POST_PIXEL')

        self.list_construction_points = []
        self.depth_location = Vector((0.0, 0.0, 0.0))
        self.surface_found = False
        self.lmb = False
        self.delta = 0
        self.temp_obj= []
        self.current_var = 0

        dbPath = get_db_path(context)
        catId = context.scene.build_props.assets_categories

        link_category_to_file(context)

        self.group_list = get_group_list_in_category(dbPath,catId)

        self.help_string = 'R/S to change distance between two props'
        context.area.header_text_set(self.help_string)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
