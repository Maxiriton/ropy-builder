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
import datetime
from sqlite3 import Error
from os.path import dirname, relpath,basename,join,split



def get_relative_file_path(pDatabaseBasePath,pFilePath):
    """Get the relative path of the current blend file to the database file"""
    relativePath = relpath(pFilePath,dirname(pDatabaseBasePath))
    return relativePath


def init_assets_database(pDatabaseBasePath):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        # Create table
        c.execute('''CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            creationDate TIMESTAMP,
            isObsolete INTEGER)''')


        c.execute('''CREATE TABLE assets (
            id INTEGER PRIMARY KEY,
            catId INTEGER NOT NULL,
            groupName TEXT NOT NULL,
            filePath TEXT NOT NULL,
            dimensionX REAL NOT NULL,
            creationDate TIMESTAMP,
            isObsolete INTEGER,
            FOREIGN KEY(catId) REFERENCES categories(id) )''')

        # Save (commit) the changes
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()

def add_new_asset(pDatabaseBasePath,pCatId,pGroupName,pFilePath,pDimX):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        t=(pCatId,pGroupName,pFilePath,0)
        c.execute("SELECT id FROM assets WHERE catId=? AND groupName =? AND filePath=? AND isObsolete=?",t)
        rows = c.fetchall()
        if len(rows) > 0:
            return ({'ERROR'},'Asset is already in database, Dickhead')

        t = (None,int(pCatId),pGroupName,pFilePath,pDimX,datetime.datetime.now(),0)
        c.execute('INSERT INTO assets VALUES (?,?,?,?,?,?,?)',t)

        # Save (commit) the changes
        conn.commit()

    except Error as e:
        print(e)
    finally:
        conn.close()

    return ({'INFO'},'Asset succesfully created in Database')



def get_total_number_of_assets(pDatabaseBasePath):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        t = (pCatId,pGroupName,pFilePath)
        c.execute('''SELECT COUNT(id) FROM assets''')

        return c.fetchone()

        # Save (commit) the changes
        conn.commit()

    except Error as e:
        print(e)
    finally:
        conn.close()

def get_all_categories(pDatabaseBasePath):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        c.execute("SELECT id,name FROM categories")
        rows = c.fetchall()
        result = []
        for row in rows:
            result.append((str(row[0]),row[1],row[1]))
        return result

    except Error as e:
        print(e)
    finally:
        conn.close()


def add_new_category(pDatabaseBasePath, pNewCategory):
    try:
        conn = sqlite3.connect(pDatabaseBasePath)
        c = conn.cursor()

        c.execute("SELECT name FROM categories WHERE name=? COLLATE NOCASE AND isObsolete=?",(pNewCategory,0))
        rows = c.fetchall()
        if len(rows) > 0:
            return ({'ERROR'},'Category is already in database, dumbass')


        t = (None,pNewCategory,datetime.datetime.now(),0)
        c.execute("INSERT INTO categories VALUES (?,?,?,?)",t)
        # Save (commit) the changes
        conn.commit()


    except Error as e:
        print(e)
    finally:
        conn.close()

    return ({'INFO'},'Category succesfully added')
