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

if "bpy" in locals():
    import imp
    imp.reload(functions)
    imp.reload(operators)
    imp.reload(ui)

else:
    from . import functions, operators, ui

import bpy
from .functions import get_groups_items



class RopyBuilderPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    libPath = bpy.props.StringProperty(
            name="Props File Path",
            subtype='FILE_PATH',
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "libPath")

class RopyBuilderProperties(bpy.types.PropertyGroup):
    """"Store properties in the active scene"""



    seed = bpy.props.IntProperty(
        name="Seed",
        description="Seed used for random generation",
        default=23,
        min=1)

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


    props_variation = bpy.props.EnumProperty(items = get_groups_items)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.build_props = bpy.props.PointerProperty(type=RopyBuilderProperties)

def unregister():
    del bpy.types.Scene.build_props

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
