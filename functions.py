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
import random
import bgl
import blf
import bmesh
import bpy_extras
import re
from mathutils import Vector, Matrix


###### ______Utils Class Definition______ ######

class construction_point():
    def __init__(self, point_coord, point_normal):
        self.point = point_coord
        if point_normal is not None:
            self.normal = point_normal
        else:
            self.normal = Vector((0.0,0.0,1.0))

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


def collect_part_variation(context,pPropName):
    result = []
    name = "prop_"+pPropName+"_var"
    p = re.compile(name+'(_\d+)?$', re.IGNORECASE)
    for obj in context.scene.objects:
        match = p.match(obj.name)

        if match is not None:
            result.append(obj)

    return result


def duplicate_props(context,pPropName):
    obj_to_dupli = context.scene.objects[pPropName]
    dupli_data = obj_to_dupli.data.copy()
    duplicata = bpy.data.objects.new("dupli_"+obj_to_dupli.name, dupli_data)
    context.scene.objects.link(duplicata)

    return duplicata

def add_empty_props(context,prop_name):
    o = bpy.data.objects.new('p_{}'.format(prop_name), None )
    context.scene.objects.link( o )
    o.empty_draw_size = 1
    o.empty_draw_type = 'PLAIN_AXES'

    return o


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


def get_props_order(context,p_edge_length,p_props_collection):
    props_order = []
    reach_end = False
    i = 0
    cur_len = 0.0
    while cur_len < p_edge_length and not reach_end:
        index = i % len(p_props_collection)
        props_order.append((index,1.0))
        cur_len += p_props_collection[index].dimensions[0]
        i +=1

    overflow = cur_len - p_edge_length
    #on scale le dernier element
    elem_size = p_props_collection[props_order[-1][0]].dimensions[0]

    scale_factor = (elem_size-overflow)/elem_size

    (index,value) = props_order[-1]
    props_order[-1] = (index,scale_factor)

    random.seed(context.scene.build_props.seed)
    random.shuffle(props_order)

    return props_order

def obj_ray_cast(obj, matrix,ray_origin,ray_target):
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

def visible_objects_and_duplis(context):
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

def get_ray_cast_result(context,coord_mouse):
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

    for obj, matrix in visible_objects_and_duplis(context):
        if obj.type != 'MESH':
            continue
        hit, normal, face_index = obj_ray_cast(obj, matrix,ray_origin,ray_target)
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

def delete_all_temp_objects(context):
    #TODO remplacer cette merde par une liste d'objet que l'on purge
    for obj in context.visible_objects:
        obj.select = False
        if obj.name.startswith('dupli_prop_'):
            obj.select = True

    bpy.ops.object.delete(use_global=True)
