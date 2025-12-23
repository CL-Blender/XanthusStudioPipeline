import bpy
import os
from bpy.types import Operator
from bpy.props import StringProperty
from .utils import (
    ensure_child_collection,
    parse_name_from_geo,
    build_default_blend_name,
    write_work_version_log,
    get_prefix,
    find_layer_collection,
)

class XST_OT_save_to_project(Operator):
    bl_idname = "xanthus_studio_tools.save_to_project"
    bl_label = "另存到專案"

    directory: StringProperty(subtype="DIR_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        props = context.scene.xst_asset_panel_props

        name = props.asset_name.strip()
        if not name:
            self.report({"ERROR"}, "無法取得名稱")
            return {"CANCELLED"}

        file_name = props.file_name.strip()
        if not file_name:
            self.report({"ERROR"}, "請輸入檔案名稱")
            return {"CANCELLED"}

        if not file_name.lower().endswith(".blend"):
            file_name += ".blend"

        type_map = {
            "CH": os.path.join("work", "char"),
            "PR": os.path.join("work", "prop"),
            "SE": os.path.join("work", "set"),
        }

        project_root = bpy.path.abspath(self.directory)
        target_dir = os.path.join(project_root, type_map[props.asset_type], name)
        os.makedirs(target_dir, exist_ok=True)

        target_path = os.path.join(target_dir, file_name)
        bpy.ops.wm.save_as_mainfile(filepath=target_path)

        # 寫入 work_version_log.txt
        write_work_version_log(
            file_path=target_path,
            asset_type=props.asset_type,
            asset_name=name,
        )

        self.report({"INFO"}, "已另存並寫入版本紀錄")
        return {"FINISHED"}

class XST_OT_create_structure(Operator):
    bl_idname = "xanthus_studio_tools.create_collection_structure"
    bl_label = "建立架構"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.xst_asset_panel_props

        name = props.asset_name.strip()
        if not name:
            self.report({"ERROR"}, "無法取得名稱")
            return {"CANCELLED"}

        asset_type = props.asset_type
        scene_col = context.scene.collection

        top = ensure_child_collection(scene_col, f"6_{asset_type}_{name}")
        tmp = ensure_child_collection(scene_col, "TMP")

        rig = ensure_child_collection(top, f"RIG_{name}")
        ensure_child_collection(rig, f"HLPS_{name}")

        meta = ensure_child_collection(tmp, "META")
        # Set collection color tag to red
        meta.color_tag = 'COLOR_01'
        ensure_child_collection(tmp, "_delete")

        # parent the reast of obj and col to tmp


        props.file_name = build_default_blend_name(asset_type, name)

        self.report({"INFO"}, "Collection 架構建立完成")
        return {"FINISHED"}
    
class XST_OT_set_name_to_selected(bpy.types.Operator):
    bl_idname = "xanthus_studio_tools.set_name_to_selected"
    bl_label = "從選取物件設定名稱"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.xst_asset_panel_props
        geo = context.active_object

        name = parse_name_from_geo(geo).strip()

        if not name:
            self.report({"ERROR"}, "無法從選取物件解析名稱")
            return {"CANCELLED"}
        
        props.asset_name = name
        self.report({"INFO"}, f"已設定名稱為：{props.asset_name}")

        return {"FINISHED"}
    
class XST_OT_set_name_to_file(bpy.types.Operator):
    bl_idname = "xanthus_studio_tools.set_name_to_file"
    bl_label = "從檔案設定名稱"

    def execute(self, context):
        props = context.scene.xst_asset_panel_props
        filepath = bpy.data.filepath

        base = os.path.basename(filepath)
        name_part = base.split("_")[1] if "_" in base else ""    
        props.asset_name = name_part.strip()
        self.report({"INFO"}, f"已設定名稱為：{props.asset_name}")

        return {"FINISHED"}

class XST_OT_load_armature_by_name(bpy.types.Operator):
    bl_idname = "xanthus_studio_tools.load_armature_by_name"
    bl_label = "載入指定名稱的 Armature"

    def execute(self, context):
        # scene = context.scene
        # scene_root = scene.collection  # Scene Collection
        # props = context.scene.xst_rigging_panel_props

        # prefixes = ("6_CH", "6_PR", "6_SE")

        # # Only direct children of Scene Collection (your requirement)
        # for top_col in scene_root.children:
        #     _, suffix = _extract_suffix(top_col.name, prefixes=prefixes)
        #     if not suffix:
        #         continue

        #     rig_col = _find_first_rig_collection(top_col)
        #     if not rig_col:
        #         continue

        #     expected_arm_name = f"RIG-{suffix}"
        #     arm = _find_armature_named(rig_col, expected_arm_name)
        #     if not arm:
        #         continue

        #     scene.xst_found_rig = arm

        #     bpy.ops.object.select_all(action='DESELECT')
        #     arm.select_set(True)
        #     context.view_layer.objects.active = arm

        #     self.report({'INFO'}, f"Found rig: {arm.name}")
        #     return {'FINISHED'}

        # scene.xst_found_rig = None
        # self.report({'WARNING'}, "No matching rig armature found.")
        # return {'CANCELLED'}

        return {"FINISHED"}

# TODO: 未完成
class XST_OT_model_export_check(bpy.types.Operator):
    bl_idname = "xanthus_studio_tools.model_export_check"
    bl_label = "模型匯出檢查"

    def execute(self, context):
        # Implement your model export check logic here
        scene = context.scene
        scene_root = scene.collection  # Scene Collection
        root_layer_collection = context.view_layer.layer_collection
        hide_collection_prefix = ["WGTS", "HLPS", "HIDE"]
        hide_collection_list = []
        

        # 顯示所有模型以便檢查

        #由檔案路徑取得名稱與類型
        filepath = bpy.data.filepath
        if not filepath:
            self.report({"ERROR"}, "請先儲存檔案以進行檢查")
            return {"CANCELLED"}
        base = os.path.basename(filepath)
        parts = base.split("_")
        if len(parts) < 2:
            self.report({"ERROR"}, "檔名格式錯誤，無法解析名稱與類型")
            return {"CANCELLED"}
        asset_type = parts[0]
        asset_name = parts[1]
        
        model_col_name = f"6_{asset_type}_{asset_name}"
        model_col = scene_root.children.get(model_col_name)
        if not model_col:
            self.report({"ERROR"}, f"找不到 Collection: {model_col_name}")
            return {"CANCELLED"}


        # Iterate through all child collections recursively and hide/unhide based on rules
        for col in model_col.children_recursive:
            # Recursively find the correct LayerCollection
            layer_collection = find_layer_collection(root_layer_collection, col)

            if not layer_collection:
                self.report({"WARNING"}, f"找不到 {col.name} 的 LayerCollection")
                continue

            # 隱藏 collections based on prefix
            if get_prefix(col.name) in hide_collection_prefix:
                layer_collection.exclude = True
                layer_collection.hide_viewport = True

                col.hide_viewport = True
                col.hide_render = True
                col.hide_select = True

                hide_collection_list.append(col.name)

                continue
            
            # 隱藏 Geo-Scatter collections
            elif col.name.startswith("Geo-Scatter"):
                if col.name == "Geo-Scatter" or col.name == "Geo-Scatter Geonode":
                    continue

                layer_collection.exclude = True
                layer_collection.hide_viewport = True

                col.hide_viewport = True
                col.hide_render = True
                col.hide_select = True

                hide_collection_list.append(col.name)

                continue

            # 顯示 collections 和 objects
            layer_collection.exclude = False
            layer_collection.hide_viewport = False

            col.hide_viewport = False
            col.hide_render = False
            col.hide_select = False

            for obj in col.objects:
                obj.hide_viewport = False
                obj.hide_render = False
                col.hide_select = False

        self.report({"INFO"}, f"隱藏的 Collection: {', '.join(hide_collection_list)}")

        # Hide objects outside of collection
        for scene_root_obj in scene_root.objects:
            scene_root_obj.hide_viewport = True
            scene_root_obj.hide_render = True

        self.report({"INFO"}, "模型匯出顯示完成")

        



        self.report({"INFO"}, "模型匯出檢查完成")
        return {"FINISHED"}
    
# TODO: 未完成
class XST_OT_rigging_export_check(bpy.types.Operator):
    bl_idname = "xanthus_studio_tools.rigging_export_check"
    bl_label = "Rigging 匯出檢查"

    def execute(self, context):
        # Implement your rigging export check logic here
        self.report({"INFO"}, "Rigging 匯出檢查完成")
        return {"FINISHED"}
    
# TODO: 未完成
class XST_OT_texture_export_check(bpy.types.Operator):
    bl_idname = "xanthus_studio_tools.texture_export_check"
    bl_label = "Texture 匯出檢查"

    def execute(self, context):
        # Implement your texture export check logic here
        self.report({"INFO"}, "Texture 匯出檢查完成")
        return {"FINISHED"}

classes = (
    XST_OT_save_to_project,
    XST_OT_create_structure,
    XST_OT_set_name_to_selected,
    XST_OT_load_armature_by_name,
    XST_OT_model_export_check,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


    