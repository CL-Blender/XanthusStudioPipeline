# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Xanthus_studio_tools",
    "author": "Jun",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

import bpy

def safe_register_class(cls):
    """安全註冊，若已註冊則先解除再重註冊"""
    try:
        bpy.utils.register_class(cls)
    except ValueError:
        try:
            bpy.utils.unregister_class(cls)
            bpy.utils.register_class(cls)
        except Exception as e:
            print(f"⚠️ 無法重新註冊 {cls.__name__}：{e}")

def safe_unregister_class(cls):
    """安全解除註冊"""
    try:
        bpy.utils.unregister_class(cls)
    except Exception:
        pass


from . import properties, utils, operators, ui, trobleshooting

modules = (
    properties,
    trobleshooting,
    utils,
    operators,
    ui,
)

def register():
    for mod in modules:
        if hasattr(mod, "register"):
            mod.register()

def unregister():
    for mod in reversed(modules):
        if hasattr(mod, "unregister"):
            mod.unregister()