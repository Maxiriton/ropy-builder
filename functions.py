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

def get_groups_items(self,context):
    collections = collect_groups_variation_distant_file(context)
    result = []
    for index,key in enumerate(collections.keys()):
        result.append((key,key,key))
    return result


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


def get_tuple(iterable, length, format=tuple):
    it = iter(iterable)
    while True:
        yield format(chain((next(it),), islice(it, length - 1)))


def collect_groups_variation_distant_file(context):
    filepath = context.user_preferences.addons[__package__].preferences.libPath

    collections = {}
    with bpy.data.libraries.load(filepath, link=False) as (data_src, data_dst):
        for GroupName in data_src.groups:
            group_parsed= GroupName.split('_')
            prop_col_name =  group_parsed[1]
            if prop_col_name in collections:
                collections[prop_col_name].append(GroupName)
            else:
                collections[prop_col_name] = [GroupName]

    return collections

def get_collection_instance(context):
    """get a list of all the groups contained in a collection"""
    col_name = context.scene.build_props.props_variation

    collections = collect_groups_variation_distant_file(context)
    result = {}
    for groupName in collections[col_name]:
        dimension = get_group_dimension_x(context,groupName)
        result[groupName] = dimension

    return result

def get_group_dimension_x(context,pGroupName):
    minx = 99999.0
    maxx = -99999.0
    try:
        group = bpy.data.groups[pGroupName]
        for obj in group.objects:
            for v in obj.bound_box:
                v_world = obj.matrix_world * Vector((v[0],v[1],v[2]))

                if v_world[0] < minx:
                    minx = v_world[0]
                if v_world[0] > maxx:
                    maxx = v_world[0]
    except:
        filepath = context.user_preferences.addons[__package__].preferences.libPath
        link = False

        # append all groups from the .blend file
        with bpy.data.libraries.load(filepath, link=link) as (data_src, data_dst):
            data_dst.groups = [pGroupName]

        for group in data_dst.groups:
            for obj in group.objects:
                for v in obj.bound_box:
                    v_world = obj.matrix_world * Vector((v[0],v[1],v[2]))

                    if v_world[0] < minx:
                        minx = v_world[0]
                    if v_world[0] > maxx:
                        maxx = v_world[0]

    return maxx-minx



def get_prop_group_instance(context, pGroupName):
    """Append a group from the library or just return the instance if it is already in scene"""

    try:
        group = bpy.data.groups[pGroupName]
        instance = bpy.data.objects.new('g_'+pGroupName, None)
        instance.dupli_type = 'GROUP'
        instance.dupli_group = group
        instance.empty_draw_size = 1
        instance.empty_draw_type = 'PLAIN_AXES'
        context.scene.objects.link(instance)
        instance.hide_select = True
        return instance
    except:
        filepath = context.user_preferences.addons[__package__].preferences.libPath
        link = False

        # append all groups from the .blend file
        with bpy.data.libraries.load(filepath, link=link) as (data_src, data_dst):
            data_dst.groups = [pGroupName]

        for group in data_dst.groups:
            instance = bpy.data.objects.new('g_'+group.name, None)
            instance.dupli_type = 'GROUP'
            instance.dupli_group = group
            context.scene.objects.link(instance)
            instance.hide_select = True
            return instance

def add_prop_instance(context,propName,variation):
    o = bpy.data.objects.new('i_{}'.format(propName), None )
    o.empty_draw_size = 1
    o.empty_draw_type = 'PLAIN_AXES'
    context.scene.objects.link(o)

    group_name = 'p_'+propName+'_'+str(int(variation))
    instance = get_prop_group_instance(context,group_name)

    instance.parent = o

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




def get_props_order(context,edge_length,p_props_collection):

    props_order = []
    reach_end = False
    i = 0
    cur_len = 0.0
    while cur_len < edge_length and not reach_end:
        index = i % len(p_props_collection)
        name = "p_"+context.scene.build_props.props_variation+'_'+str(index+1)
        props_order.append((name,1.0))
        cur_len += p_props_collection[name]
        i +=1

    overflow = cur_len - edge_length
    #on scale le dernier element
    elem_size = p_props_collection[props_order[-1][0]]

    scale_factor = (elem_size-overflow)/elem_size

    (last_element_name,value) = props_order[-1]
    props_order[-1] = (last_element_name,scale_factor)

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

def visibles_objects_without_builder_props(context):
    """Loop over (object, matrix) pairs (mesh only)"""
    for obj in context.visible_objects:
        if obj.type == 'MESH':
            if obj.parent is not None:
                print(obj.parent.name)
            yield (obj, obj.matrix_world.copy())


def visible_objects_and_duplis(context):
    """Loop over (object, matrix) pairs (mesh only)"""

    for obj in context.visible_objects:
        if obj.type == 'MESH':
            yield (obj, obj.matrix_world.copy())

        if obj.dupli_type != 'NONE':
            obj.dupli_list_create(context.scene)
            for dob in obj.dupli_list:
                obj_dupli = dob.object
                if obj_dupli.type == 'MESH':
                    yield (obj_dupli, dob.matrix.copy())

        obj.dupli_list_clear()

def get_ray_cast_result(context,coord_mouse,use_all_objects=False):
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


    obj_list = None
    if use_all_objects:
        obj_list = visible_objects_and_duplis(context)
    else:
        obj_list = visibles_objects_without_builder_props(context)

    for obj, matrix in obj_list:
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

def remove_orphan_props_func(context):
    for obj in context.scene.objects:
        if obj.type == 'EMPTY' and obj.name.startswith('g_'):
            bpy.data.objects.remove(obj,True)


def delete_all_temp_objects(context,obj_to_delete):
    for obj in context.visible_objects:
        obj.select = False

    for name in obj_to_delete:
        print('coucou' +name)
        context.scene.objects[name].hide_select = False
        context.scene.objects[name].select = True

    bpy.ops.object.delete(use_global=True)
