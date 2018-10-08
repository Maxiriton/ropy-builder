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
from .draw import draw_callback_area_px

class ModalFillPolyOperator(bpy.types.Operator):
    """Fill an area with props"""
    bl_idname = "ropy.modal_fill_poly"
    bl_label = "Fill Area with Props"

    help_string = ''


    def add_prop(self,context,location,rotation):
        groupName = self.group_list[self.current_var][1]
        e = add_prop_instance(context,groupName)

        loc_mat = Matrix.Translation(location)

        scale_mat = Matrix.Scale(1,4,(1,0,0)) * Matrix.Scale(1,4,(0,1,0)) * Matrix.Scale(1,4,(0,0,1))
        if context.scene.build_props.paint_random_scale:
            factor = random.uniform(context.scene.build_props.paint_random_min_max[0], context.scene.build_props.paint_random_min_max[1])
            scale_mat = Matrix.Scale(factor,4,(1,0,0)) * Matrix.Scale(factor,4,(0,1,0)) * Matrix.Scale(factor,4,(0,0,1))

        v0 = Vector(( 0.0,0,1.0 ))
        orig_rot_mat = v0.rotation_difference(rotation).to_matrix().to_4x4()

        mat_rot =  mathutils.Matrix.Rotation(0, 4, rotation)
        if context.scene.build_props.paint_random_rotation:
            factor = random.uniform(-context.scene.build_props.paint_random_max_angle,context.scene.build_props.paint_random_max_angle)
            mat_rot = mathutils.Matrix.Rotation(factor, 4, rotation)

        e.matrix_world = loc_mat * mat_rot * orig_rot_mat * scale_mat
        #we need to update the index for next addition
        self.current_var += 1
        self.current_var = self.current_var % len(self.group_list)
        self.allobjs.append(e.name)

    def update_mouse_action(self,context):
        delete_temp_objects(context,self.allobjs)
        self.allobjs = []

        if len(self.list_construction_points) < 3 :
            return
        obj,rdn_points = define_random_points_in_ngon(context,self.list_construction_points,context.scene.build_props.props_density)
        self.random_points = rdn_points

        for pnt in self.random_points:
            self.add_prop(context,pnt,Vector(( 0,0,1.0 )))


        self.allobjs.append(obj.name)


    def execute(self, context):
        print('Coucou')

    def modal(self, context, event):
        context.area.tag_redraw()
        region = context.region
        rv3d = context.space_data.region_3d

        if event.type == 'MOUSEMOVE':
            coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            self.mouse_path = coord_mouse

            # get the ray from the viewport and mouse
            best_hit,best_obj,best_normal,best_face_index = get_ray_cast_result(context,coord_mouse)

            self.surface_found = False
            if best_hit is not None:
                self.surface_found = True
                self.surface_normal = best_hit + best_normal
                self.surface_hit = best_hit

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':

                coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
                best_hit,best_obj,best_normal,best_face_index = get_ray_cast_result(context,coord_mouse)

                new_point = None
                if best_obj is not None:
                    mouse_loc_3d = view3d_utils.region_2d_to_location_3d(
                        region, rv3d, coord_mouse, best_hit)
                    new_point = construction_point(mouse_loc_3d,best_normal)
                else:
                    mouse_loc_3d = view3d_utils.region_2d_to_location_3d(
                        region, rv3d, coord_mouse, self.depth_location)
                    new_point = construction_point(mouse_loc_3d,None)
                self.list_construction_points.append(new_point)
                self.depth_location = self.list_construction_points[-1].point

                self.update_mouse_action(context)
            elif event.value == 'RELEASE':
                pass

        elif event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                if not self.list_construction_points:
                    self.depth_location = Vector((0.0, 0.0, 0.0))
                elif len(self.list_construction_points) == 1:
                    self.list_construction_points.pop()
                    self.depth_location = Vector((0.0, 0.0, 0.0))
                else:
                    self.list_construction_points.pop()
                    self.depth_location = self.list_construction_points[-1].point
                self.update_mouse_action(context)
            elif event.value == 'RELEASE':
                pass

        elif event.type  in {'S'} and event.value == 'PRESS':
            context.scene.build_props.props_density +=  1
            self.update_mouse_action(context)

        elif event.type in {'R'} and event.value == 'PRESS':
            context.scene.build_props.props_density +=  -1
            self.update_mouse_action(context)

        elif event.type in {'RET'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.area.header_text_set()
            self.execute(context)
            return {'FINISHED'}

        elif event.type in {'ESC'}:
            context.area.header_text_set()
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.list_construction_points[:] = []
            self.depth_location = Vector((0.0, 0.0, 0.0))
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_area_px, args, 'WINDOW', 'POST_PIXEL')

            #We iniatialize all the variables we are going to use
            self.mouse_path = []
            self.list_construction_points = []
            self.depth_location = Vector((0.0, 0.0, 0.0))
            self.surface_found = False
            self.allobjs = []
            self.random_points = []
            self.current_var = 0

            dbPath = get_db_path(context)
            catId = context.scene.build_props.assets_categories

            link_category_to_file(context)

            self.group_list = get_group_list_in_category(dbPath,catId)
            context.window_manager.modal_handler_add(self)

            self.help_string = 'R/S to get change props density'
            context.area.header_text_set(self.help_string)
            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
