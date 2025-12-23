import bpy
from bpy.types import Operator, Panel, UIList, PropertyGroup
from bpy.props import (
    StringProperty,
    EnumProperty,
    CollectionProperty,
    IntProperty,
    PointerProperty,
    BoolProperty,
)

# ----------------------------
# Data Model
# ----------------------------

def _level_icon(level: str) -> str:
    return {
        "INFO": "INFO",
        "WARNING": "ERROR",   # Blender does not have a distinct WARNING icon everywhere; ERROR reads well in UI
        "ERROR": "CANCEL",
    }.get(level, "DOT")

def _target_icon(target_type: str) -> str:
    return {
        "OBJECT": "OBJECT_DATA",
        "BONE": "BONE_DATA",
        "MATERIAL": "MATERIAL",
        "NONE": "DOT",
    }.get(target_type, "DOT")


class XST_LogEntry(PropertyGroup):
    level: EnumProperty(
        name="Level",
        items=[
            ("INFO", "Info", ""),
            ("WARNING", "Warning", ""),
            ("ERROR", "Error", ""),
        ],
        default="ERROR",
    ) # type: ignore

    message: StringProperty(name="Message")# type: ignore
    details: StringProperty(name="Details")# type: ignore

    target_type: EnumProperty(
        name="Target Type",
        items=[
            ("OBJECT", "Object", ""),
            ("BONE", "Bone", ""),
            ("MATERIAL", "Material", ""),
            ("NONE", "None", ""),
        ],
        default="NONE",
    )# type: ignore

    # Targets (use pointers where possible)
    target_object: PointerProperty(type=bpy.types.Object)# type: ignore
    target_armature: PointerProperty(type=bpy.types.Object)  # should be an ARMATURE object in practice# type: ignore
    target_bone: StringProperty(name="Bone Name")# type: ignore
    target_material: PointerProperty(type=bpy.types.Material)# type: ignore

    # Convenience display (optional)
    target_label: StringProperty(name="Target Label")# type: ignore


class XST_LogState(PropertyGroup):
    entries: CollectionProperty(type=XST_LogEntry)# type: ignore
    index: IntProperty(default=-1)# type: ignore

    filter_text: StringProperty(
        name="Filter",
        description="Filter log entries by message/target text",
        default="",
    )# type: ignore

    auto_select_on_add: BoolProperty(
        name="Auto Focus On Add",
        description="When adding a new log entry, automatically focus it",
        default=False,
    )# type: ignore


def xst_log_state(context) -> XST_LogState:
    return context.window_manager.xst_log


# ----------------------------
# Logger helper (NOT registered)
# ----------------------------

class XST_Logger:
    def __init__(self, context):
        self.state = xst_log_state(context)

    def clear(self):
        self.state.entries.clear()
        self.state.index = -1

    def log(
        self,
        message: str,
        details: str = "",
        level: str = "ERROR",
        *,
        target_type: str = "NONE",
        target_object=None,
        target_armature=None,
        target_bone: str = "",
        target_material=None,
        target_label: str = "",
    ) -> XST_LogEntry:
        e = self.state.entries.add()
        e.message = message
        e.details = details
        e.level = level

        e.target_type = target_type
        e.target_object = target_object
        e.target_armature = target_armature
        e.target_bone = target_bone
        e.target_material = target_material
        e.target_label = target_label

        self.state.index = len(self.state.entries) - 1
        return e


# ----------------------------
# Operators
# ----------------------------

class XST_OT_log_clear(Operator):
    bl_idname = "xst.log_clear"
    bl_label = "Clear Log"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        XST_Logger(context).clear()
        return {"FINISHED"}


class XST_OT_log_focus(Operator):
    bl_idname = "xst.log_focus"
    bl_label = "Focus Log Target"
    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty(default=-1)# type: ignore

    def execute(self, context):
        state = xst_log_state(context)
        idx = self.index if self.index >= 0 else state.index
        if idx < 0 or idx >= len(state.entries):
            return {"CANCELLED"}

        e = state.entries[idx]

        # Focus OBJECT
        if e.target_type == "OBJECT" and e.target_object:
            obj = e.target_object
            if obj.name in context.view_layer.objects:
                bpy.ops.object.select_all(action="DESELECT")
                obj.select_set(True)
                context.view_layer.objects.active = obj
                # View framing is optional; it requires a 3D view context to be present
                if bpy.ops.view3d.view_selected.poll():
                    bpy.ops.view3d.view_selected()
            return {"FINISHED"}

        # Focus BONE (armature + bone name)
        if e.target_type == "BONE" and e.target_armature and e.target_bone:
            arm_obj = e.target_armature
            if not arm_obj or arm_obj.type != "ARMATURE":
                return {"CANCELLED"}

            bpy.ops.object.select_all(action="DESELECT")
            arm_obj.select_set(True)
            context.view_layer.objects.active = arm_obj

            # Switch to pose mode if possible
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode="POSE")

            bone = arm_obj.data.bones.get(e.target_bone)
            if bone:
                # Select bone and make it active
                for b in arm_obj.data.bones:
                    b.select = False
                bone.select = True
                arm_obj.data.bones.active = bone
                if bpy.ops.view3d.view_selected.poll():
                    bpy.ops.view3d.view_selected()
                return {"FINISHED"}

            return {"CANCELLED"}

        # Focus MATERIAL (select objects using it, best-effort)
        if e.target_type == "MATERIAL" and e.target_material:
            mat = e.target_material
            users = []
            for obj in context.scene.objects:
                if obj.type == "MESH" and obj.data and hasattr(obj.data, "materials"):
                    if mat in obj.data.materials:
                        users.append(obj)

            if users:
                bpy.ops.object.select_all(action="DESELECT")
                for obj in users:
                    obj.select_set(True)
                context.view_layer.objects.active = users[0]
                if bpy.ops.view3d.view_selected.poll():
                    bpy.ops.view3d.view_selected()
                return {"FINISHED"}

            return {"CANCELLED"}

        return {"CANCELLED"}


class XST_OT_check_selected_missing_materials(Operator):
    bl_idname = "xst.check_missing_materials"
    bl_label = "Check Selected: Missing Materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        logger = XST_Logger(context)

        for obj in context.selected_objects:
            if obj.type != "MESH":
                continue
            mats = getattr(obj.data, "materials", None)
            if not mats or len(mats) == 0:
                logger.log(
                    "Mesh has no material slots",
                    details=f"Object '{obj.name}' has no materials assigned.",
                    level="WARNING",
                    target_type="OBJECT",
                    target_object=obj,
                    target_label=obj.name,
                )

        return {"FINISHED"}


# ----------------------------
# UIList + Panel
# ----------------------------

class XST_UL_log_entries(UIList):
    bl_idname = "XST_UL_log_entries"

    def filter_items(self, context, data, propname):
        state = xst_log_state(context)
        flt_flags = []
        flt_neworder = []

        items = getattr(data, propname)
        text = (state.filter_text or "").strip().lower()

        if not text:
            flt_flags = [self.bitflag_filter_item] * len(items)
            return flt_flags, flt_neworder

        for e in items:
            hay = " ".join([
                e.message or "",
                e.target_label or "",
                (e.target_object.name if e.target_object else ""),
                (e.target_armature.name if e.target_armature else ""),
                (e.target_bone or ""),
                (e.target_material.name if e.target_material else ""),
            ]).lower()

            flt_flags.append(self.bitflag_filter_item if text in hay else 0)

        return flt_flags, flt_neworder

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index=0):
        e: XST_LogEntry = item

        row = layout.row(align=True)
        row.label(text="", icon=_level_icon(e.level))
        row.label(text=e.message or "", icon=_target_icon(e.target_type))

        if e.target_label:
            row.label(text=e.target_label, icon="LINKED")

        op = row.operator("xst.log_focus", text="", icon="VIEWZOOM")
        op.index = index


class XST_PT_log(Panel):
    bl_label = "Debug Log"
    bl_idname = "XST_PT_log"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Xanthus Tools"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        state = xst_log_state(context)

        header = layout.row(align=True)
        header.prop(state, "filter_text", text="", icon="VIEWZOOM")
        header.operator("xst.log_clear", text="", icon="TRASH")

        layout.template_list(
            "XST_UL_log_entries",
            "",
            state,
            "entries",
            state,
            "index",
            rows=6,
        )

        layout.prop(state, "auto_select_on_add")

        layout.separator()
        layout.operator("xst.check_missing_materials", icon="SHADING_RENDERED")


# ----------------------------
# Registration
# ----------------------------

classes = (
    XST_LogEntry,
    XST_LogState,
    XST_OT_log_clear,
    XST_OT_log_focus,
    XST_OT_check_selected_missing_materials,
    XST_UL_log_entries,
    XST_PT_log,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.xst_log = PointerProperty(type=XST_LogState)

def unregister():
    del bpy.types.WindowManager.xst_log

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
