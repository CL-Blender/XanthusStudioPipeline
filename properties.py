import bpy
from bpy.props import EnumProperty, StringProperty, PointerProperty
from bpy.types import Operator, Panel, PropertyGroup

class XST_asset_props(PropertyGroup):

    asset_type: EnumProperty(
        name="類型",
        items=[
            ("CH", "CH（角色）", ""),
            ("PR", "PR（道具）", ""),
            ("SE", "SE（場景）", ""),
        ],
        default="CH",
    ) # type: ignore

    asset_name: StringProperty(
        name="名稱（備用）",
        description="無法從 GEO-xxx 解析時使用",
        default="",
    ) # type: ignore

    file_name: StringProperty(
        name="檔案名稱",
        description="另存的 blend 檔名（可修改）",
        default="",
        maxlen=255,
    ) # type: ignore

    

class XST_rigging_props(PropertyGroup):
    rig_armature: PointerProperty(
        name="Rig Armature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    ) # type: ignore

    meta_armature: PointerProperty(
        name="Meta Armature",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'ARMATURE'
    ) # type: ignore


classes = (
    XST_asset_props,
    XST_rigging_props,
    XST_LogEntry,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.xst_asset_panel_props = PointerProperty(type=XST_asset_props)
    bpy.types.Scene.xst_rigging_panel_props = PointerProperty(type=XST_rigging_props)

def unregister():
    del bpy.types.Scene.xst_asset_panel_props
    del bpy.types.Scene.xst_rigging_panel_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)