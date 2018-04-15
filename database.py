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

import sqlite3

def init_assets_database(pDatabaseBasePath):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        # Create table
        c.execute('''CREATE TABLE [IF NOT EXISTS] categories (
            id int NOT NULL PRIMARY KEY,
            name text NOT NULL)''')


        c.execute('''CREATE TABLE [IF NOT EXISTS] assets (
            id int NOT NULL PRIMARY KEY,
            catId int NOT NULL ,
            groupName text NOT NULL,
            filePath text NOT NULL,
            CONSTRAINT fkCatId FOREIGN KEY catId REFERENCES categories(id) )''')




        # Save (commit) the changes
        conn.commit()
    except Error as e:
        print(e)
    finally:
        conn.close()

def insert_new_asset(pDatabaseBasePath,pCatId,pGroupName,pFilePath):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        t = (pCatId,pGroupName,pFilePath)
        c.execute('INSERT INTO assets VALUES (?,?,?)',t)

        # Save (commit) the changes
        conn.commit()

    except Error as e:
        print(e)
    finally:
        conn.close()
