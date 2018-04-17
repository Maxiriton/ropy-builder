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
import mathutils
from  math import radians

from .functions import *
from .database import *
from .ui import draw_callback_line_px,draw_callback_brush_px,draw_callback_change_prop_px

class AddAssetToDatabase(bpy.types.Operator):
    """Add the current group to the database"""
    bl_idname = "ropy.add_asset_to_database"
    bl_label = "Add to database"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        dbPath = context.user_preferences.addons[__package__].preferences.dbPath
        curFile = bpy.data.filepath

        relFilePath = get_relative_file_path(dbPath,curFile)
        catId = context.scene.build_props.assets_categories
        groupName = context.scene.build_props.current_groups_in_files
        groupDimX= get_group_dimension_x_new(context,groupName)

        status, message = add_new_asset(dbPath,catId,groupName,relFilePath,groupDimX)
        self.report(status,message)
        return {'FINISHED'}

class LinkGroupsToFile(bpy.types.Operator):
    """Link all the groups from the current category to the blender file"""
    bl_idname = "ropy.link_groups_to_file"
    bl_label = "Link category to file"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        dbPath = context.user_preferences.addons[__package__].preferences.dbPath
        catId = context.scene.build_props.assets_categories

        rows = get_group_list_in_category(dbPath,catId)
        for row in rows:
            filePath=get_blender_file_abs_path(dbPath, row[2])
            link_groups_to_file(context,filePath,row[1])

        return {'FINISHED'}


class AddCategoryToDatabase(bpy.types.Operator):
    """Add a new asset category into the database"""
    bl_idname = "ropy.add_cat_to_database"
    bl_label = "Create a new category"

    cat_name = bpy.props.StringProperty(name="cat_name")

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        db_path = context.user_preferences.addons[__package__].preferences.dbPath
        status, message = add_new_category(db_path,self.cat_name)
        self.report(status,message)
        return {'FINISHED'}

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self,"cat_name")


class InitDatabase(bpy.types.Operator):
    """Initialize the database"""
    bl_idname = "ropy.init_database"
    bl_label = "Initialize Database"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        cur_path = bpy.path.abspath('//assets.db')
        init_assets_database(cur_path)
        return {'FINISHED'}


class GenerateRoomOperator(bpy.types.Operator):
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


class ChangePropVariation(bpy.types.Operator):
    """Change the variation of a prop"""
    bl_idname = "ropy.change_prop_variation"
    bl_label = " Change prop variation"

    def change_prop(self,context):
        obj = context.scene.objects.active
        transforms = obj.matrix_world

        self.index +=1
        self.index = self.index % len(self.group_list)

        new_prop  = add_prop_instance(context,self.group_list[self.index][1])
        print(transforms)
        new_prop.select = True
        new_prop.matrix_world = transforms
        context.scene.objects.active = new_prop

        bpy.data.objects.remove(obj, True)


    @classmethod
    def poll(cls,context):
        actif = context.scene.objects.active
        return context.mode == 'OBJECT' and actif is not None and actif.name.startswith('i_')

    def modal(self,context,event):
        context.area.tag_redraw()
        region = context.region
        rv3d = context.space_data.region_3d

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.change_prop(context)
        elif event.type  in {'R'} and event.value == 'PRESS':
            self.change_prop(context)
        elif event.type in {'ESC'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_change_prop_px, args, 'WINDOW', 'POST_PIXEL')

        dbPath = context.user_preferences.addons[__package__].preferences.dbPath

        obj = context.scene.objects.active
        _groupName = extract_groupName(obj)
        self.group_list = get_group_list_from_group(dbPath,_groupName)

        #we are looking for the index of the group in list
        _found = False
        self.index = 0
        while not _found:
            if self.group_list[self.index][1] == _groupName:
                _found = True
            else:
                self.index +=1


        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ModalDrawBrushOperator(bpy.types.Operator):
    """Draw props on scene"""
    bl_idname = "ropy.modal_draw_brush"
    bl_label = "Draw Props on surfaces"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


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

        self.temp_obj.append(e)
        #we need to update the index for next addition
        self.current_var += 1
        self.current_var = self.current_var % len(self.group_list)

    def modal(self,context,event):
        context.area.tag_redraw()
        region = context.region
        rv3d = context.space_data.region_3d

        if event.type == 'MOUSEMOVE':
            coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
            self.mouse_path = coord_mouse

            # get the ray from the viewport and mouse
            best_hit,best_obj,best_normal,best_face_index = get_ray_cast_result(context,coord_mouse,context.scene.build_props.paint_on_all_objects)

            self.surface_found = False
            if best_hit is not None:
                self.surface_found = True
                self.surface_normal = best_hit + best_normal
                self.surface_hit = best_hit

                if self.lmb: #if the left button is pressed
                    self.delta += (self.previous_impact - self.surface_hit).length

                    #add a object if the distance between the previous one is too short
                    if self.delta > context.scene.build_props.brush_distance:
                        self.add_prop(context,best_hit,best_normal)
                        self.delta = 0.0

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

        self.list_construction_points = []
        self.depth_location = Vector((0.0, 0.0, 0.0))
        self.surface_found = False
        self.lmb = False
        self.delta = 0
        self.temp_obj= []
        self.current_var = 1

        dbPath = context.user_preferences.addons[__package__].preferences.dbPath
        catId = context.scene.build_props.assets_categories

        self.group_list = get_group_list_in_category(dbPath,catId)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class ModalDrawLineOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "ropy.modal_draw_line"
    bl_label = "Line filled Assets"


    def update_mouse_action(self,context):
        delete_temp_objects(context,self.allobjs)
        self.allobjs = []
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


            propsOrder = get_props_order(context,edge_length,self.group_list)
            print(propsOrder)
            curent_distance = 0.0
            for dimX,groupName, scaleValue in propsOrder:
                dupli = add_prop_instance(context,groupName)
                dupli.scale[0] = scaleValue
                dupli.rotation_euler = rot
                dupli.location = vert_0 + direction_x.normalized()*curent_distance
                curent_distance += dimX*scaleValue
                self.allobjs.append(dupli.name)

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
            context.scene.build_props.seed +=  1
            self.update_mouse_action(context)

        elif event.type in {'R'} and event.value == 'PRESS':
            context.scene.build_props.seed +=  -1
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
            args = (self, context)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_line_px, args, 'WINDOW', 'POST_PIXEL')

            #We iniatialize all the variables we are going to use
            self.mouse_path = []
            self.list_construction_points = []
            self.depth_location = Vector((0.0, 0.0, 0.0))
            self.surface_found = False
            self.allobjs = []

            dbPath = context.user_preferences.addons[__package__].preferences.dbPath
            catId = context.scene.build_props.assets_categories

            self.group_list = get_group_list_in_category(dbPath,catId)
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
