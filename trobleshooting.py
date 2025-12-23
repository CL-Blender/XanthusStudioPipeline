import bpy
from bpy.props import StringProperty
from bpy.types import Operator, Panel   

class XST_LogEntry(bpy.types.PropertyGroup):
    icon: bpy.props.StringProperty(default='ERROR')# type: ignore
    description_short: bpy.props.StringProperty(name="Short Description")# type: ignore
    description: bpy.props.StringProperty(name="Full Details")# type: ignore
    
    # New flexible targeting fields
    target_name: bpy.props.StringProperty(name="Target Name")# type: ignore
    target_type: bpy.props.EnumProperty(
        items=[
            ('OBJECT', "Object", "Focus an Object"),
            ('BONE', "Bone", "Focus a Bone inside an Armature"),
            ('MATERIAL', "Material", "Select a Material"),
            ('NONE', "None", "")
        ],
        default='NONE'
    )# type: ignore

class XST_UL_log_entry_slots(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon_value, active_data, active_propname):
        log = item
        
        # Use a map to choose the icon based on the target type
        icon_map = {
            'OBJECT': 'OBJECT_DATA',
            'BONE': 'BONE_DATA',
            'MATERIAL': 'MATERIAL',
            'NONE': 'ERROR'
        }
        icon = icon_map.get(log.target_type, 'DOT')
        
        row = layout.row(align=True)
        # Show the short description and the icon
        row.label(text=log.description_short, icon=icon)
        
        # If there's a target name, show it on the right side for clarity
        if log.target_name:
            row.label(text=log.target_name, icon='LINKED')

class XST_Logger:
    def __init__(self):
        # Always point to the window manager
        self.wm = bpy.context.window_manager

    def log(self, title, detail="", icon='ERROR', target="", target_type='NONE'):
        entry = self.wm.my_tool_logs.add()
        entry.description_short = title
        entry.description = detail
        entry.icon = icon
        entry.target_name = target
        entry.target_type = target_type
        return entry

    def clear(self):
        self.wm.my_tool_logs.clear()
        self.wm.my_tool_log_index = 0

class XST_PT_log(bpy.types.Panel):
    bl_label = "Generation Log"
    bl_idname = "XST_PT_log"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "Xanthus Tools"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        # 1. Draw the actual UIList
        # template_list(idname, list_id, dataptr, propname, active_dataptr, active_propname)
        layout.template_list(
            "MYTOOL_UL_log_entry_slots", "the_log_list", 
            obj, "my_tool_logs", 
            obj, "my_tool_log_index"
        )

classes = (
    XST_LogEntry,  
    XST_UL_log_entry_slots,
    XST_PT_log,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Object.my_tool_logs = bpy.props.CollectionProperty(type=XST_LogEntry) # type: ignore
    bpy.types.Object.my_tool_log_index = bpy.props.IntProperty(name="Log Index", default=0) # type: ignore

def unregister():
    del bpy.types.Object.my_tool_logs
    del bpy.types.Object.my_tool_log_index
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)