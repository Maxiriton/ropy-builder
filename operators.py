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

from .functions import *
from .ui import draw_callback_line_px, draw_callback_brush_px

class Generate_room_operator(bpy.types.Operator):
    """Generate walls and roof from selection"""
    bl_idname = "edit.generate_room"
    bl_label = "Generate Room"
    bl_options = {'REGISTER', 'UNDO'}

    height = bpy.props.FloatProperty(
            name="Height",
            description="Box Height",
            min=0.01,
            max=100.0,
            default=1.0,
            )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "height")

    def execute(self, context):
        generate_room(context,self.height)
        return {'FINISHED'}

class collect_part_variation_operator(bpy.types.Operator):
    """Collect props groups from library file"""
    bl_idname = "ropy.collect_distant_groups"
    bl_label = "Collect Props Variation"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        collect_groups_variation_distant_file(context)
        return {'FINISHED'}



class ModalDrawBrushOperator(bpy.types.Operator):
    """Draw props on scene"""
    bl_idname = "view3d.modal_draw_brush"
    bl_label = "Draw Props on surfaces"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def modal(self,context,event):
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

                if self.lmb: #if the left button is pressed
                    self.delta += (self.previous_impact - self.surface_hit).length

                    #add a object if the distance between the previous one is too short
                    if self.delta > context.scene.build_props.brush_distance:
                        e = add_prop_instance(context,'rock')
                        e.location = best_hit
                        self.delta = 0.0

                    print(str(self.delta))
                    self.previous_impact = self.surface_hit



        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.lmb = True
                coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
                # get the ray from the viewport and mouse
                best_hit,best_obj,best_normal,best_face_index = get_ray_cast_result(context,coord_mouse)
                if best_hit is not None:
                    self.previous_impact = best_hit
                    self.delta = 0

                    e = add_prop_instance(context,'rock')
                    # e = add_empty_props(context,'Emile')
                    e.location = best_hit
                    #TODO Get correct rotation !!!!

            elif event.value == 'RELEASE':
                self.lmb = False
        elif event.type  in {'S'} and event.value == 'PRESS':
            context.scene.build_props.brush_distance +=  0.1
        elif event.type in {'R'} and event.value == 'PRESS':
            context.scene.build_props.brush_distance +=  -0.1
        elif event.type in {'ESC'}:
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
            draw_callback_line_px, args, 'WINDOW', 'POST_PIXEL')


        self.mouse_path = []
        self.list_construction_points = []
        self.depth_location = Vector((0.0, 0.0, 0.0))
        self.surface_found = False
        self.lmb = False



        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ModalDrawLineOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "view3d.modal_draw_line"
    bl_label = "Simple Modal View3D Operator"


    def update_mouse_action(self,context):
        delete_all_temp_objects(context)
        #on recupere la liste des variations de props
        props = collect_part_variation(context,'fence')
        vert_0 = None

        for i in range(len(self.list_construction_points)):
            vert_0 = self.list_construction_points[i].point

            try:
                vert_1 = self.list_construction_points[i+1].point
            except:
                break
            edge_length = (vert_0-vert_1).length

            direction_x = vert_1-vert_0

            v0 = Vector(( 1.0,0,0 ))
            #TODO get correct rotation angle !!!!!
            rot = v0.rotation_difference( direction_x ).to_euler()

            props_order = get_props_order(context,edge_length,props)
            curent_distance = 0.0
            for index,value in enumerate(props_order):
                to_dupli_name = props[value[0]].name
                dupli = duplicate_props(context,to_dupli_name)
                dupli.scale[0] = value[1]
                dupli.rotation_euler = rot
                dupli.location = vert_0 + direction_x.normalized()*curent_distance
                curent_distance += props[value[0]].dimensions[0]*value[1]

    def execute(self, context):
        # Create a mesh object to store polygon line
        mesh_obj = bpy.data.meshes.new("meshLine")
        # create a object data for mesh object
        obj_crt = bpy.data.objects.new("meshLine", mesh_obj)

        # link object to scene
        context.scene.objects.link(obj_crt)
        context.scene.objects.active = obj_crt

        # Now copy the mesh object to bmesh
        bme = bmesh.new()
        bme.from_mesh(obj_crt.data)
        matx = obj_crt.matrix_world.inverted()

        # Add vertices
        list_verts = []

        for i in self.list_construction_points:
            bme.verts.new(matx * i.point)
            bme.verts.index_update()
            bme.verts.ensure_lookup_table()
            list_verts.append(bme.verts[-1])

        # Add edges to bmesh
        total_edge = len(list_verts)

        for j in range(total_edge - 1):
            bme.edges.new((list_verts[j], list_verts[(j + 1) % total_edge]))
            bme.edges.index_update()

        # add this data to bmesh object
        bme.to_mesh(obj_crt.data)
        bme.free()

        # intialize all variables zero Value
        self.list_construction_points[:] = []
        list_verts[:] = []
        self.depth_location = Vector((0.0, 0.0, 0.0))
        return {'FINISHED'}

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
                    mouse_loc_3d = bpy_extras.view3d_utils.region_2d_to_location_3d(
                        region, rv3d, coord_mouse, best_hit)
                    new_point = construction_point(mouse_loc_3d,best_normal)
                else:
                    mouse_loc_3d = bpy_extras.view3d_utils.region_2d_to_location_3d(
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
            context.scene.builder_editor.seed +=  1
            self.update_mouse_action(context)

        elif event.type in {'R'} and event.value == 'PRESS':
            context.scene.builder_editor.seed +=  -1
            self.update_mouse_action(context)

        elif event.type in {'RET'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.execute(context)
            return {'FINISHED'}

        elif event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            self.list_construction_points[:] = []
            self.depth_location = Vector((0.0, 0.0, 0.0))
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            # the arguments we pass the the callback

            args = (self, context)

            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_line_px, args, 'WINDOW', 'POST_PIXEL')


            self.mouse_path = []
            self.list_construction_points = []
            self.depth_location = Vector((0.0, 0.0, 0.0))
            self.surface_found = False
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
