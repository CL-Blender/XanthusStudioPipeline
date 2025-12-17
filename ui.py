import bpy
import os
import getpass
from datetime import datetime
from bpy.props import EnumProperty, StringProperty, PointerProperty, BoolProperty

class XST_PT_preferences(bpy.types.AddonPreferences):
    # Preferences 面板設定
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__ or __name__

    asset_panel: BoolProperty(
        name="顯示 Asset 工具面板",
        default=True,
        description="在 3D 視窗的側邊欄顯示 Asset 工具面板",
    ) # type: ignore
    texturePanel: BoolProperty(
        name="顯示 Texture 工具面板",  
        default=True,
        description="在 3D 視窗的側邊欄顯示 Texture 工具面板",
    ) # type: ignore

    riggingPanel: BoolProperty(
        name="顯示 Rigging 工具面板",
        default=True,
        description="在 3D 視窗的側邊欄顯示 Rigging 工具面板",
    ) # type: ignore

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.prop(self, "asset_panel")

        box = layout.box()
        box.prop(self, "texturePanel")

        box = layout.box() 
        box.prop(self, "riggingPanel")

class XST_PT_assetpanel(bpy.types.Panel):
    bl_label = "Asset 工具"
    bl_idname = "XST_PT_assetpanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Xanthus Tools"

    #判斷是否顯示UI
    @classmethod
    def poll(cls, context):
        addon = context.preferences.addons.get(__package__ or __name__)
        if not addon:
            return False
        prefs = addon.preferences
        return prefs.asset_panel

    def draw(self, context):
        layout = self.layout
        props = context.scene.xst_asset_panel_props

        layout.prop(props, "asset_type")
        layout.prop(props, "asset_name")
        layout.operator("xanthus_studio_tools.set_name_to_selected", icon="RESTRICT_SELECT_OFF")

        layout.operator("xanthus_studio_tools.create_collection_structure", icon="OUTLINER_COLLECTION")

        layout.separator()
        layout.prop(props, "file_name")
        layout.label(text="只需選專案路徑即可", icon="INFO")
        layout.operator("xanthus_studio_tools.save_to_project", icon="FILE_FOLDER")

class XST_PT_riggingpanel(bpy.types.Panel):
    bl_label = "Rigging 工具"
    bl_idname = "XST_PT_riggingpanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Xanthus Tools"

    @classmethod
    def poll(cls, context):
        addon = context.preferences.addons.get(__package__ or __name__)
        if not addon:
            return False
        prefs = addon.preferences
        return prefs.riggingPanel

    def draw(self, context):
        layout = self.layout
        props = context.scene.xst_rigging_panel_props

        layout.prop(props, "rig_armature", text="RigArmature", icon='OUTLINER_OB_ARMATURE')
        layout.prop(props, "meta_armature", text="MetaArmature", icon='OUTLINER_OB_ARMATURE')
        #load armature button
        layout.operator("xanthus_studio_tools.load_armature_by_name", icon="OUTLINER_OB_ARMATURE")

class XST_PT_texturepanel(bpy.types.Panel):
    bl_label = "Texture 工具"
    bl_idname = "XST_PT_texturepanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Xanthus Tools"

    @classmethod
    def poll(cls, context):
        addon = context.preferences.addons.get(__package__ or __name__)
        if not addon:
            return False
        prefs = addon.preferences
        return prefs.texturePanel

    def draw(self, context):
        layout = self.layout
        layout.operator("xanthus_studio_tools.load_armature_by_name", icon="OUTLINER_OB_ARMATURE")


classes = ( 
    XST_PT_preferences,
    XST_PT_assetpanel,
    XST_PT_riggingpanel,
    XST_PT_texturepanel,
)   

def register():
    for cls in classes: 
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
