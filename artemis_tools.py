# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Ropy Builder",
    "author": "Henri Hebeisen",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "3D View, ",
    "description": "Level editor in Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
    }

import bpy
import random
import bgl
import blf
import bmesh
import bpy_extras
from mathutils import Vector, Matrix
from itertools import chain, islice
from math import degrees

###### Class Definition ######

class construction_point():
    def __init__(self, point_coord, point_normal):
        self.point = point_coord
        if point_normal is not None: 
            self.normal = point_normal
        else:
            self.normal = Vector((0.0,0.0,1.0))




class Builder_Properties(bpy.types.PropertyGroup):
    """Store properties in the active scene"""

    spc_NbrPoints = bpy.props.IntProperty(
        name="Number of Points",
        description="Number of generated points",
        default=23,
        min=1)

    spc_SearchName = bpy.props.StringProperty(
        name="Name to match",
        description="Find all objects with this name",
        default="")

    spc_UseActiveObject = bpy.props.BoolProperty(
        name="Use active object",
        description="Use active object's volume as reference volume for objects detection",
        default=True)

    spc_SmallObjTolerance = bpy.props.IntProperty(
        name="volume tolerance",
        description="percentage of volume tolerance used for object detection",
        default= 20,
        min=0,
        max=100)

    spc_GroupName = bpy.props.StringProperty(
        name="Group Target",
        description="Group Target to select",
        default="")

    spc_ConfPath = bpy.props.StringProperty(
      name = "File Path",
      default = "",
      description = "Define the root path of the project",
      subtype = 'FILE_PATH')

    spc_SelectionVolume = bpy.props.FloatVectorProperty(
        name ="Volume Dimension",
        unit = 'AREA',
        precision = 3,
        default=(0.2, 0.2, 0.2))


###### ______Utils Functions Definition______ ######

def area_of_type(type_name):
    for area in bpy.context.screen.areas:
        if area.type == type_name:
            return area

def get_3d_view():
    return area_of_type('VIEW_3D').spaces[0]

def get_faces_with_normal(pNormal, pTolerance):
    """Return a list of faces that have similar normal"""
    #TODO
    return []
    
def draw_callback_px(self, context):
    region = context.region
    rv3d = context.space_data.region_3d
    # print("mouse points", len(self.mouse_path))

    # Draw Points
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.8, 0.0, 1.0)
    bgl.glPointSize(5.0)
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

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

def get_tuple(iterable, length, format=tuple):
    it = iter(iterable)
    while True:
        yield format(chain((next(it),), islice(it, length - 1)))


###### ______Functions Definition______ ######

def unwrap_mesh_to_box(context,pScale):
    bpy.ops.uv.cube_project()


def generate_room(context,height):
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height)})
    #on déplie tout le monde
    #on separe les murs et le toit
    unwrap_mesh_to_box(context,0.1)

def orient_object_to_normal(context,pNormVect,pObject):
    ori = pObject.orientation
    mat = Matrix(ori[0], ori[1], ori[2])

    pos = pObject.position
    vec1 = Vector(pos[0], pos[1], pos[2]) # Convert the position into a vector
    vec2 = Vector(0,0,-1) # Make a vector for the end point of the ray (below the object)
    vec3 = vec2 * mat # Convert the end point into local coords of the ob
    vec4 = vec1 + vec3 # Add the end point to the position vector to account for translation
        
    ray = pObject.rayCast(vec4, ob, 15, '') # Cast a ray
        
    if ray[0]: 
        pObject.alignAxisToVect(ray[2], 2, 1) # Align the object to the hit normal of the ray


###### ______UI Definition______ ######

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
        row.operator("view3d.modal_operator", text="Draw Props", icon='IPO_ELASTIC')

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



###### ______Operator Definition______ ######


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
        
class ModalDrawLineOperator(bpy.types.Operator):
    """Draw a line with the mouse"""
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"

    def obj_ray_cast(self,obj, matrix,ray_origin,ray_target):
        """Wrapper for ray casting that moves the ray into object space"""

        # get the ray relative to the object
        matrix_inv = matrix.inverted()
        ray_origin_obj = matrix_inv * ray_origin
        ray_target_obj = matrix_inv * ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        # cast the ray
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)

        if success:
            return location, normal, face_index
        else:
            return None, None, None

    def visible_objects_and_duplis(self,context):
        """Loop over (object, matrix) pairs (mesh only)"""

        for obj in context.visible_objects:
            if obj.type == 'MESH':
                yield (obj, obj.matrix_world.copy())

            if obj.dupli_type != 'NONE':
                obj.dupli_list_create(scene)
                for dob in obj.dupli_list:
                    obj_dupli = dob.object
                    if obj_dupli.type == 'MESH':
                        yield (obj_dupli, dob.matrix.copy())

            obj.dupli_list_clear()

    def get_ray_cast_result(self,context,coord_mouse):
        region = context.region
        rv3d = context.space_data.region_3d
        # get the ray from the viewport and mouse
        view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, rv3d, coord_mouse)
        ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, coord_mouse)

        ray_target = ray_origin + view_vector

        # cast rays and find the closest object
        best_length_squared = -1.0
        best_obj = None
        best_hit = None #best hit location
        best_normal = None
        best_face_index = None

        for obj, matrix in self.visible_objects_and_duplis(context):
            if obj.type != 'MESH':
                continue 
            hit, normal, face_index = self.obj_ray_cast(obj, matrix,ray_origin,ray_target)
            if hit is not None:
                hit_world = matrix * hit
                length_squared = (hit_world - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = obj
                    best_hit = hit_world

                    rot_quaternion = matrix.decompose()[1]
                    best_normal = rot_quaternion.to_matrix() *  normal
                    best_face_index = face_index

        return best_hit,best_obj,best_normal,best_face_index

    def add_cube(self,context):
        # Create an empty mesh and the object.
        mesh = bpy.data.meshes.new('Basic_Cube')
        basic_cube = bpy.data.objects.new("Basic_Cube", mesh)

        # Add the object into the scene.
        context.scene.objects.link(basic_cube)
        # context.scene.objects.active = basic_cube
        # basic_cube.select = True

        # Construct the bmesh cube and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(mesh)
        bm.free()

        return basic_cube

    def delete_all_temp_objects(self,context):

        for obj in context.visible_objects:
            obj.select = False
            if obj.name.startswith('Basic_Cube'):
                obj.select = True
        
        bpy.ops.object.delete(use_global=True)



    def update_mouse_action(self,context):
        #on calcule la taille totale du strip
        tot_len = 0
        self.delete_all_temp_objects(context)
        if len(self.list_construction_points) == 0:
            return tot_len

        vert_0 = None

        for i in range(len(self.list_construction_points)):
            vert_0 = self.list_construction_points[i].point

            try: 
                vert_1 = self.list_construction_points[i+1].point
                tot_len += (vert_0-vert_1).length

                direction_x = vert_1-vert_0

                v0 = Vector(( 1.0,0,0 ))

                rot = v0.rotation_difference( direction_x ).to_euler()
                print(rot)

                cube  = self.add_cube(context)
                cube.rotation_euler = rot
                cube.location = vert_0


            except: 
                break

        if self.surface_found:
            tot_len += (vert_0-self.surface_hit).length



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
            best_hit,best_obj,best_normal,best_face_index = self.get_ray_cast_result(context,coord_mouse)

            self.surface_found = False
            if best_hit is not None:
                self.surface_found = True
                self.surface_normal = best_hit + best_normal
                self.surface_hit = best_hit

            

        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                
                coord_mouse = Vector((event.mouse_region_x, event.mouse_region_y))
                best_hit,best_obj,best_normal,best_face_index = self.get_ray_cast_result(context,coord_mouse)

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

        elif event.type in {'RIGHTMOUSE','RET'}:
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
                draw_callback_px, args, 'WINDOW', 'POST_PIXEL')


            self.mouse_path = []
            self.list_construction_points = []
            self.depth_location = Vector((0.0, 0.0, 0.0))
            self.surface_found = False
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

def register():
    bpy.utils.register_class(Builder_Properties)
    bpy.utils.register_class(ModalDrawLineOperator
    )
    bpy.utils.register_class(Generate_room_operator)

    bpy.utils.register_class(VIEW3D_PT_BuilderEditorPanel)
    bpy.utils.register_class(VIEW3D_PT_BuilderEditor_edit_Panel)

    bpy.types.Scene.builder_editor = bpy.props.PointerProperty(type=Builder_Properties)



def unregister():
    bpy.utils.unregister_class(Builder_Properties)
    bpy.utils.unregister_class(TextSearchOperator)
    bpy.utils.unregister_class(ModalDrawOperator)

    bpy.utils.unregister_class(VIEW3D_PT_BuilderEditorPanel)
    bpy.utils.unregister_class(VIEW3D_PT_BuilderEditor_edit_Panel)

    del bpy.types.Scene.builder_editor


if __name__ == "__main__":
    register()
