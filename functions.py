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
from .database import *


###### ______Utils Class Definition______ ######

class construction_point():
    def __init__(self, point_coord, point_normal):
        self.point = point_coord
        if point_normal is not None:
            self.normal = point_normal
        else:
            self.normal = Vector((0.0,0.0,1.0))

###### ______Utils Functions Definition______ ######

def get_db_categories(self,context):
    """Get a list of all the current categories stored in database"""
    db_path = context.user_preferences.addons[__package__].preferences.dbPath
    return get_all_categories(db_path)


def get_group_list(self,context):
    """Get an enum of all the groups in the file"""
    result = []
    for group in bpy.data.groups:
        result.append((group.name,group.name,group.name))

    return result

def link_groups_to_file(context,pFilePath,pGroupName):
    with bpy.data.libraries.load(pFilePath, link=True, relative=True) as (data_from, data_to):
        data_to.groups = [pGroupName]

def link_category_to_file(context):
    dbPath = context.user_preferences.addons[__package__].preferences.dbPath
    catId = context.scene.build_props.assets_categories

    rows = get_group_list_in_category(dbPath,catId)
    for row in rows:
        filePath=get_blender_file_abs_path(dbPath, row[2])
        link_groups_to_file(context,filePath,row[1])

def set_new_groupName(pGroupName):
    """Increment an existing groupName like that:
        rocher => rocher_2
        rocher_23 => rocher_24"""
    rex = re.compile('_\d+$')

    m = rex.search(pGroupName)
    if m:
        var = m.group(0)
        varValue = int(var[1:])
        pGroupName = pGroupName[:-len(var)]+"_"+str(varValue+1)
    else:
        pGroupName = '%s_2' %pGroupName

    return pGroupName



def extract_groupName(pObj):
    """Extract the GroupName from the name of an object"""
    rex = re.compile('\.\d{3}$')

    groupName = pObj.name[2:]
    if rex.search(pObj.name):
        groupName = groupName[:-4]

    return groupName

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

def get_group_dimension_x(context,pGroupName):
    minx = 99999.0
    maxx = -99999.0

    group = bpy.data.groups[pGroupName]
    for obj in group.objects:
        for v in obj.bound_box:
            v_world = obj.matrix_world * Vector((v[0],v[1],v[2]))

            if v_world[0] < minx:
                minx = v_world[0]
            if v_world[0] > maxx:
                maxx = v_world[0]

    return maxx-minx

def get_group_min_x_offset(context,pGroupName):
    minX = 99999.0

    group = bpy.data.groups[pGroupName]
    for obj in group.objects:
        for v in obj.bound_box:
            v_world = obj.matrix_world * Vector((v[0],v[1],v[2]))

            if v_world[0] < minX:
                minX = v_world[0]

    centerX = group.dupli_offset[0]

    return centerX-minX


def add_prop_instance(context,groupName):
    """Add a new empty to the scene with a dupligroup on it.
       We assume that the group is already linked to scene!"""

    group = bpy.data.groups[groupName]
    o = bpy.data.objects.new('i_{}'.format(groupName), None )
    o.dupli_type = 'GROUP'
    o.dupli_group = group
    o.empty_draw_size = 1
    o.empty_draw_type = 'PLAIN_AXES'
    context.scene.objects.link(o)

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




def get_props_order(context,edge_length,rows):
    """Used for ModalDrawLineOperator.
        Return a list containing group, its X dimension and its potential
        scale value. The list is randomized based on the current context
        seed value"""
    #row schema : ID,GROUP_NAME,FILE_PATH,GROUP_LENGTH,OFFSET_X
    propsOrder = []
    i = 0
    curLen = 0.0
    cur_index = 0
    while curLen < edge_length:
        cur_index = i % len(rows)
        dimX = rows[cur_index][3]
        offsetX = rows[cur_index][4]
        groupName = rows[cur_index][1]
        propsOrder.append((dimX,groupName,1.0,offsetX)) #Last value is scale_value
        curLen += dimX
        i +=1

    overflow = curLen - edge_length
    elem_size = rows[cur_index][3]
    scale_factor = (elem_size-overflow)/elem_size

    (dimX,groupName,scale_value,offsetX) = propsOrder[-1]
    propsOrder[-1] = (dimX,groupName,scale_factor,offsetX)

    random.seed(context.scene.build_props.seed)
    random.shuffle(propsOrder)

    return propsOrder

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


def delete_temp_objects(context,obj_to_delete):
    for obj in context.visible_objects:
        obj.select = False

    for name in obj_to_delete:
        context.scene.objects[name].hide_select = False
        context.scene.objects[name].select = True

    bpy.ops.object.delete(use_global=True)
