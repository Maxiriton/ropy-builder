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
from os.path import join, splitext

from .functions import *
from .database import *


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
        groupName = context.scene.build_props.current_groups_in_files

        if is_group_in_database(dbPath,groupName,relFilePath):
            self.report({'ERROR'},'Asset is already in database')
            return {'FINISHED'}

        catId = context.scene.build_props.assets_categories
        groupDimX= get_group_dimension_x(context,groupName)
        groupOffsetX= get_group_min_x_offset(context,groupName)

        if is_groupName_used_in_other_file(dbPath,groupName,relFilePath):
            #TODO Make sure it's the biggestName in current scene too
            biggestName = get_biggest_groupName(dbPath,groupName)
            newGroupName = set_new_groupName(biggestName)
            #we have to rename the current group with its new name
            bpy.data.groups[groupName].name = newGroupName
            status, message = add_new_asset(dbPath,catId,newGroupName,relFilePath,groupDimX,groupOffsetX)
            status = {'WARNING'}
        else:
            status, message = add_new_asset(dbPath,catId,groupName,relFilePath,groupDimX,groupOffsetX)

        self.report(status,message)
        return {'FINISHED'}


class UpdateAssetInDatabase(bpy.types.Operator):
    """Update the current group in the database"""
    bl_idname = "ropy.update_asset_to_database"
    bl_label = "Update in database"

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        dbPath = context.user_preferences.addons[__package__].preferences.dbPath
        groupName = context.scene.build_props.current_groups_in_files

        catId = context.scene.build_props.assets_categories
        groupDimX= get_group_dimension_x(context,groupName)
        groupOffsetX= get_group_min_x_offset(context,groupName)

        status, message = update_asset(dbPath,catId,groupName,groupDimX,groupOffsetX)
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
        link_category_to_file(context)
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

    dbPath =  bpy.props.StringProperty(
                name="Database Path",
                subtype='FILE_PATH')

    dbName = bpy.props.StringProperty(
                name="Database Name",
                subtype='FILE_NAME',
                default='assets')

    setAsDefault = bpy.props.BoolProperty(name='set_default',default = False)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        relPath = join(self.dbPath,splitext(self.dbName)[0]+'.db')
        absPath= bpy.path.abspath(relPath)
        status, message =  init_assets_database(absPath)

        self.report(status,message)
        if status is not {'ERROR'}:
            if self.setAsDefault:
                context.user_preferences.addons[__package__].preferences.dbPath = absPath
        return {'FINISHED'}

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self,"dbPath")
        row = layout.row()
        row.prop(self,"dbName")
        row = layout.row()
        row.prop(self,"setAsDefault",text="Use the database as default database")


class ExportScene(bpy.types.Operator):
    """Export the current scene"""
    bl_idname = "ropy.export_scene"
    bl_label = "Export Scene"

    use_selection = bpy.props.BoolProperty(name='use_selection',default = False)
    only_meshes = bpy.props.BoolProperty(name="only_meshes",default = False)
    export_instances = bpy.props.BoolProperty(name="export_instances", default = True)


    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def invoke(self,context,event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        instancePrefix = context.user_preferences.addons[__package__].preferences.instancePrefix

        for obj in context.scene.objects:
            if obj.type == 'EMPTY' and obj.name.startswith(instancePrefix):
                obj.dupli_type = 'NONE'

        exportPath = context.scene.build_props.export_path

        file_name = bpy.path.display_name_from_filepath(bpy.context.blend_data.filepath)
        exportPath = join(exportPath,file_name+'.fbx')

        obj_types = {'EMPTY','MESH'}
        if not self.only_meshes:
            obj_types = {'EMPTY','CAMERA','LAMP','ARMATURE','MESH'}

        bpy.ops.export_scene.fbx(filepath=exportPath,use_selection=self.use_selection,object_types= obj_types)


        if self.export_instances:
            selected_ojbects = context.selected_objects
            for obj in context.scene.objects:
                obj.select = False
            for group in bpy.data.groups:
                if group.users > 0:
                    #we have to export this group
                    o = add_prop_instance(context,group.name)
                    o.select = True

                    exportPath = context.scene.build_props.export_path
                    exportPath = join(exportPath,extract_groupName(o)+".fbx")

                    bpy.ops.export_scene.fbx(filepath=exportPath,use_selection=True)

                    bpy.data.objects.remove(o, True)


        for obj in context.scene.objects:
            if obj.type == 'EMPTY' and obj.name.startswith(instancePrefix):
                obj.dupli_type = 'GROUP'

        return {'FINISHED'}

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self,"use_selection",text="Export only selected objects")
        row = layout.row()
        row.prop(self,"only_meshes",text="Export only meshes and empties")
        row = layout.row()
        row.prop(self,"export_instances",text="Export instances as separate files")


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
