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
    "version": (0, 2),
    "blender": (2, 78, 0),
    "location": "3D View, ",
    "description": "Level editor in Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
    }

if "bpy" in locals():
    import imp
    imp.reload(functions)

    imp.reload(ui)
    imp.reload(database)
    imp.reload(operators)
    imp.reload(ops_fillarea)
    imp.reload(ops_paintbrush)
    imp.reload(ops_linebrush)
    imp.reload(ops_changeprops)
    imp.reload(ops_precise_instance)
else:
    from . import functions, operators, ui,database
    from . import ops_fillarea,ops_linebrush,ops_paintbrush,ops_changeprops
    from . import ops_precise_instance

import bpy
from .functions import get_db_categories,get_group_list



class RopyBuilderPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    dbPath = bpy.props.StringProperty(
            name="Database Path",
            subtype='FILE_PATH',
            )

    instancePrefix = bpy.props.StringProperty(
            name="Instance Prefix",
            default="i_")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "dbPath")
        layout.prop(self, "instancePrefix")

class RopyBuilderProperties(bpy.types.PropertyGroup):
    """"Store properties in the active scene"""

    seed = bpy.props.IntProperty(
        name="Seed",
        description="Seed used for random generation",
        default=23,
        min=1)

    line_scale_factor = bpy.props.FloatProperty(
        name="Scale Factor",
        description="Props scale factor",
        default=1.0)

    brush_distance = bpy.props.FloatProperty(
        name="Distance",
        description="Distance between two objects",
        default=1,
        min=0.01)

    paint_on_all_objects = bpy.props.BoolProperty(
        name="Paint on all objects",
        description="Use all objects to paint",
        default=False)

    paint_random_scale = bpy.props.BoolProperty(
        name="Randomize scale",
        description="randomize the scale of painted object",
        default=True)


    paint_random_min_max = bpy.props.FloatVectorProperty(
        name = 'Scale limits',
        description = 'Minimum and maximumscale',
        default = (0.1,1.0),
        size=2,
        soft_min=0.05,
        soft_max = 2.0)

    paint_random_rotation = bpy.props.BoolProperty(
        name ="Randomize rotation",
        description="Randomize the rotation around objects Z axis",
        default= True)

    paint_random_max_angle = bpy.props.FloatProperty(
        name = "Rotation max",
        description = "Maximum Rotation angle",
        subtype = "ANGLE",
        unit = "ROTATION",
        default = 0.5)

    assets_categories = bpy.props.EnumProperty(
        items = get_db_categories,
        name = "Categories",
        description = "Categories stored in database")

    current_groups_in_files = bpy.props.EnumProperty(
        items = get_group_list,
        name = "Group",
        description = "List of groups in current blender file")

    export_path = bpy.props.StringProperty(
        name="Export Path",
        subtype='DIR_PATH',
        )

    props_density = bpy.props.FloatProperty(
        name="Density",
        default=1,
        min=0
    )


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.build_props = bpy.props.PointerProperty(type=RopyBuilderProperties)

def unregister():
    del bpy.types.Scene.build_props

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
