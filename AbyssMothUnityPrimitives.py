bl_info = {
    "name": "AbyssMoth Unity-friendly Primitives",
    "author": "AbyssMoth",
    "version": (1, 3, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Add",
    "description": "Unity Mesh menu (1m), underscore naming, and real Shift+D override in User keymap",
    "category": "3D View",
}

import re
import bpy
from bpy.props import FloatProperty, BoolProperty
from bpy.types import AddonPreferences

addonKeymaps = []
disabledDefaultKeymaps = []


class AbyssMothUnityPrimitivesPreferences(AddonPreferences):
    bl_idname = __name__

    defaultSizeMeters: FloatProperty(
        name="Default Size (meters)",
        default=1.0,
        min=0.0001,
        description="Target size for cube/plane/grid. Spheres use radius = size/2",
    )

    bindUnityDuplicateHotkey: BoolProperty(
        name="Bind Unity Duplicate to Shift+D (Object Mode)",
        default=True,
        description="Binds Shift+D in Object Mode to Unity Duplicate (underscore naming)",
    )

    disableDefaultDuplicateHotkey: BoolProperty(
        name="Disable default Duplicate Objects (Shift+D)",
        default=True,
        description="Disables Blender default Shift+D in Object Mode so Unity Duplicate always triggers",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "defaultSizeMeters")
        layout.separator()
        layout.prop(self, "bindUnityDuplicateHotkey")
        layout.prop(self, "disableDefaultDuplicateHotkey")


def GetAddonPreferences(context):
    addon = context.preferences.addons.get(__name__)
    if addon is None:
        return None
    return addon.preferences


def GetSize(context):
    prefs = GetAddonPreferences(context)
    if prefs is None:
        return 1.0
    return float(prefs.defaultSizeMeters)


def StripTrailingDotNumbers(name):
    return re.sub(r"(\.\d{3})+$", "", name)


def SplitRootAndIndex(name):
    match = re.match(r"^(.*?)(?:_(\d{3}))?$", name)
    if match is None:
        return name, 0

    root = match.group(1)
    indexText = match.group(2)
    if indexText is None:
        return root, 0

    try:
        return root, int(indexText)
    except Exception:
        return root, 0


def BuildRootMaxIndexMap():
    result = {}

    for name in bpy.data.objects.keys():
        base = StripTrailingDotNumbers(name)
        root, index = SplitRootAndIndex(base)

        current = result.get(root, 0)
        if index > current:
            result[root] = index
        else:
            result.setdefault(root, current)

    return result


def MakeUniqueName(root):
    rootMaxIndex = BuildRootMaxIndexMap()

    maxIndex = rootMaxIndex.get(root, 0)
    rootExists = root in bpy.data.objects

    if not rootExists and maxIndex == 0:
        return root

    value = maxIndex + 1
    candidate = f"{root}_{value:03d}"
    while candidate in bpy.data.objects:
        value += 1
        candidate = f"{root}_{value:03d}"

    return candidate


def RenameObjectAndData(obj, desiredName):
    obj.name = desiredName

    if obj.data is not None and getattr(obj.data, "users", 1) == 1:
        obj.data.name = desiredName


def RenameActiveObject(rootName):
    obj = bpy.context.active_object
    if obj is None:
        return

    uniqueName = MakeUniqueName(rootName)
    RenameObjectAndData(obj, uniqueName)


def DisableDefaultDuplicateShiftD():
    prefs = GetAddonPreferences(bpy.context)
    if prefs is None or not prefs.disableDefaultDuplicateHotkey:
        return

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    if kc is None:
        return

    km = kc.keymaps.get("Object Mode")
    if km is None:
        return

    for kmi in km.keymap_items:
        if not kmi.active:
            continue

        if kmi.type != "D" or kmi.value != "PRESS" or not kmi.shift:
            continue

        if kmi.idname in {"object.duplicate_move", "object.duplicate_move_linked"}:
            disabledDefaultKeymaps.append((kmi, True))
            kmi.active = False


def RestoreDefaultDuplicateShiftD():
    for kmi, wasActive in disabledDefaultKeymaps:
        try:
            kmi.active = wasActive
        except Exception:
            pass
    disabledDefaultKeymaps.clear()


def RegisterShiftDUserKeymap():
    prefs = GetAddonPreferences(bpy.context)
    if prefs is None or not prefs.bindUnityDuplicateHotkey:
        return

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    if kc is None:
        return

    km = kc.keymaps.get("Object Mode")
    if km is None:
        km = kc.keymaps.new(name="Object Mode", space_type="EMPTY", region_type="WINDOW")

    kmi = km.keymap_items.new(AbyssMothUnityDuplicateMove.bl_idname, type="D", value="PRESS", shift=True)
    addonKeymaps.append((km, kmi))


def UnregisterUserKeymaps():
    for km, kmi in addonKeymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addonKeymaps.clear()


class AbyssMothUnityDuplicateMove(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_duplicate_move"
    bl_label = "Unity Duplicate (Shift+D)"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if context.mode != "OBJECT":
            return {"CANCELLED"}

        if len(context.selected_objects) == 0:
            return {"CANCELLED"}

        bpy.ops.object.duplicate()

        rootMaxIndex = BuildRootMaxIndexMap()

        for obj in context.selected_objects:
            base = StripTrailingDotNumbers(obj.name)
            root, _ = SplitRootAndIndex(base)

            value = rootMaxIndex.get(root, 0) + 1
            newName = f"{root}_{value:03d}"

            while newName in bpy.data.objects:
                value += 1
                newName = f"{root}_{value:03d}"

            rootMaxIndex[root] = value
            RenameObjectAndData(obj, newName)

        bpy.ops.transform.translate("INVOKE_DEFAULT")
        return {"FINISHED"}


class AbyssMothUnityAddCube(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_cube"
    bl_label = "Cube (1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        bpy.ops.mesh.primitive_cube_add(size=size)
        RenameActiveObject("Cube")
        return {"FINISHED"}


class AbyssMothUnityAddPlane(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_plane"
    bl_label = "Plane (1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        bpy.ops.mesh.primitive_plane_add(size=size)
        RenameActiveObject("Plane")
        return {"FINISHED"}


class AbyssMothUnityAddGrid(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_grid"
    bl_label = "Grid (1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        bpy.ops.mesh.primitive_grid_add(size=size)
        RenameActiveObject("Grid")
        return {"FINISHED"}


class AbyssMothUnityAddUvSphere(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_uv_sphere"
    bl_label = "UV Sphere (Ø1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        radius = size * 0.5
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius)
        RenameActiveObject("UvSphere")
        return {"FINISHED"}


class AbyssMothUnityAddIcoSphere(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_ico_sphere"
    bl_label = "Ico Sphere (Ø1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        radius = size * 0.5
        bpy.ops.mesh.primitive_ico_sphere_add(radius=radius)
        RenameActiveObject("IcoSphere")
        return {"FINISHED"}


class AbyssMothUnityAddCylinder(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_cylinder"
    bl_label = "Cylinder (Ø1m, H1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        radius = size * 0.5
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=size)
        RenameActiveObject("Cylinder")
        return {"FINISHED"}


class AbyssMothUnityAddCone(bpy.types.Operator):
    bl_idname = "abyssmoth.unity_add_cone"
    bl_label = "Cone (Ø1m, H1m)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        size = GetSize(context)
        radius = size * 0.5
        bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0.0, depth=size)
        RenameActiveObject("Cone")
        return {"FINISHED"}


class VIEW3D_MT_abyssMothUnityMesh(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_abyssMothUnityMesh"
    bl_label = "Unity Mesh"

    def draw(self, context):
        layout = self.layout

        layout.operator(AbyssMothUnityAddCube.bl_idname, icon="MESH_CUBE")
        layout.operator(AbyssMothUnityAddPlane.bl_idname, icon="MESH_PLANE")
        layout.operator(AbyssMothUnityAddGrid.bl_idname, icon="MESH_GRID")

        layout.separator()

        layout.operator(AbyssMothUnityAddUvSphere.bl_idname, icon="MESH_UVSPHERE")
        layout.operator(AbyssMothUnityAddIcoSphere.bl_idname, icon="MESH_ICOSPHERE")

        layout.separator()

        layout.operator(AbyssMothUnityAddCylinder.bl_idname, icon="MESH_CYLINDER")
        layout.operator(AbyssMothUnityAddCone.bl_idname, icon="MESH_CONE")

        layout.separator()

        layout.operator(AbyssMothUnityDuplicateMove.bl_idname, icon="DUPLICATE")


def DrawUnityMeshRootEntry(self, context):
    self.layout.menu(VIEW3D_MT_abyssMothUnityMesh.bl_idname, icon="MESH_CUBE")


classes = (
    AbyssMothUnityPrimitivesPreferences,
    AbyssMothUnityDuplicateMove,
    AbyssMothUnityAddCube,
    AbyssMothUnityAddPlane,
    AbyssMothUnityAddGrid,
    AbyssMothUnityAddUvSphere,
    AbyssMothUnityAddIcoSphere,
    AbyssMothUnityAddCylinder,
    AbyssMothUnityAddCone,
    VIEW3D_MT_abyssMothUnityMesh,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_add.prepend(DrawUnityMeshRootEntry)

    DisableDefaultDuplicateShiftD()
    RegisterShiftDUserKeymap()


def unregister():
    UnregisterUserKeymaps()
    RestoreDefaultDuplicateShiftD()

    bpy.types.VIEW3D_MT_add.remove(DrawUnityMeshRootEntry)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
