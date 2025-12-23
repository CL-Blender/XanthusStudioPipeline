import bpy
import os   
import getpass
from datetime import datetime



def ensure_child_collection(parent, name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
    if col.name not in parent.children:
        parent.children.link(col)
    return col

def parse_name_from_geo(obj):
    if obj and obj.name.startswith("GEO-") and len(obj.name) > 4:
        return obj.name[4:]
    elif obj:
        return obj.name
    else:
        return ""


def unlink_object_from_all_collections(obj):
    for c in list(obj.users_collection):
        try:
            c.objects.unlink(obj)
        except RuntimeError:
            pass

def build_default_blend_name(asset_type, asset_name):
    return f"{asset_type}_{asset_name}_V01_mod-B01.blend"


def write_work_version_log(file_path, asset_type, asset_name):
    user = getpass.getuser()
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 從檔名解析版本（抓 V01）
    version = "UNKNOWN"
    base = os.path.basename(file_path)
    for part in base.split("_"):
        if part.startswith("V") and part[1:].isdigit():
            version = part
            break

    log_path = os.path.join(
        os.path.dirname(file_path),
        "work_version_log.txt"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("-" * 60 + "\n")
        f.write(f"User    : {user}\n")
        f.write(f"Time    : {time_str}\n")
        f.write(f"Asset   : {asset_type}_{asset_name}\n")
        f.write(f"Version : {version}\n")
        f.write(f"Path    : {file_path}\n")
        f.write("-" * 60 + "\n\n")

def find_layer_collection(layer_collection, target_collection):
    """ Recursively search for the layer_collection that corresponds to a given collection. """
    if layer_collection.collection == target_collection:
        return layer_collection
    for child in layer_collection.children:
        found = find_layer_collection(child, target_collection)
        if found:
            return found
    return None

def get_prefix(name):
    # get the prefix before the first underscore
    if "_" in name:
        return name.split("_")[0]
    elif "-" in name:
        return name.split("-")[0]
    return None

def register():
    pass

def unregister():
    pass