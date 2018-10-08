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
import blf
import bgl
from bpy_extras import view3d_utils


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

        loc_1 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.surface_normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)
        bgl.glDisable(bgl.GL_BLEND)


def draw_callback_precise_brush(self,context):
    region = context.region
    rv3d = context.space_data.region_3d

    if self.surface_found: #if there is a surface under mouse cursor
        bgl.glEnable(bgl.GL_BLEND)
        bgl.glColor4f(1.0, 1.0, 0.0, 1.0)
        bgl.glLineWidth(1)
        bgl.glEnable(bgl.GL_LINE)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

        loc_1 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.surface_normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)

    #on trace une ligne entre l'endroit ou on a position l'object et la souris
    if self.lmb:
        bgl.glEnable(bgl.GL_LINE)
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glColor4f(1.0, 0.0, 1.0, 1.0)
        bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])
        root = view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.previous_impact)
        bgl.glVertex2f(root[0], root[1])
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
    # bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

    for x in self.list_construction_points:
        loc_1 = view3d_utils.location_3d_to_region_2d(
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
        loc_1 = view3d_utils.location_3d_to_region_2d(
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
        loc_1 = view3d_utils.location_3d_to_region_2d(
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

        root = view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point)
        bgl.glVertex2f(root[0], root[1])
        tip = view3d_utils.location_3d_to_region_2d(
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

        loc_1 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.surface_normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)
        bgl.glDisable(bgl.GL_BLEND)

def draw_callback_area_px(self, context):
    region = context.region
    rv3d = context.space_data.region_3d

    # Draw Points
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.8, 0.0, 1.0)
    bgl.glPointSize(5.0)
    bgl.glBegin(bgl.GL_POINTS)
    # bgl.glVertex2f(self.mouse_path[0], self.mouse_path[1])

    for x in self.list_construction_points:
        loc_1 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point)
        bgl.glVertex2f(loc_1[0], loc_1[1])



    for x in self.random_points:
        point = view3d_utils.location_3d_to_region_2d(
            region, rv3d,x)
        bgl.glVertex2f(point[0], point[1])


    bgl.glEnd()
    bgl.glDisable(bgl.GL_BLEND)

    # Draw Normal point
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.3, 0.8, 0.8, 1.0)
    bgl.glPointSize(2.0)
    bgl.glBegin(bgl.GL_POINTS)

    for x in self.list_construction_points:
        loc_1 = view3d_utils.location_3d_to_region_2d(
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
        loc_1 = view3d_utils.location_3d_to_region_2d(
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

        root = view3d_utils.location_3d_to_region_2d(
            region, rv3d, x.point)
        bgl.glVertex2f(root[0], root[1])
        tip = view3d_utils.location_3d_to_region_2d(
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

        loc_1 = view3d_utils.location_3d_to_region_2d(
            region, rv3d, self.surface_normal)
        bgl.glVertex2f(loc_1[0], loc_1[1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STRIP)
        bgl.glDisable(bgl.GL_BLEND)




    # restore opengl defaults
    # bgl.glLineWidth(1)
    # bgl.glDisable(bgl.GL_BLEND)
    # bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
