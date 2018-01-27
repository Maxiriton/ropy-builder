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

class RopyBuilderPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    libPath = bpy.props.StringProperty(
            name="Props File Path",
            subtype='FILE_PATH',
            )
    number = bpy.props.IntProperty(
            name="Example Number",
            default=4,
            )
    boolean = bpy.props.BoolProperty(
            name="Example Boolean",
            default=False,
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our addon")
        layout.prop(self, "libPath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")

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


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.build_props = bpy.props.PointerProperty(type=RopyBuilderProperties)

def unregister():
    del bpy.types.Scene.build_props

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
