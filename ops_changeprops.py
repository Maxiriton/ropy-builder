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

from .functions import *
from .database import *
from .draw import draw_callback_change_prop_px

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

        dbPath = get_db_path(context)

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
