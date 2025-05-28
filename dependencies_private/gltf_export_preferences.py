# SPDX-FileCopyrightText: 2018-2022 The glTF-Blender-IO authors
#
# SPDX-License-Identifier: Apache-2.0

# Large portions of this file are taken from Blender's io_scene_gltf2 core addon.
# See https://github.com/blender/blender/blob/b80f1f5322cdd2e040c70bbbd78ec83870d05b81/scripts/addons_core/io_scene_gltf2/__init__.py#L1828
# Some properties have been removed, such as "Include" settings since this add-on has its own include logic.
# The purpose is to add similar export settings to the Roblox add-on that exist in Blender's gltf exporter,
# since the same export operation is used for both.

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty
from bpy.types import AddonPreferences


def on_export_action_filter_changed(self, context):
    if self.export_action_filter is True:
        bpy.types.Scene.gltf_action_filter = bpy.props.CollectionProperty(type=GLTF2_filter_action)
        bpy.types.Scene.gltf_action_filter_active = bpy.props.IntProperty()

        for action in bpy.data.actions:
            if id(action) not in [id(item.action) for item in bpy.data.scenes[0].gltf_action_filter]:
                item = bpy.data.scenes[0].gltf_action_filter.add()
                item.keep = True
                item.action = action

    else:
        bpy.data.scenes[0].gltf_action_filter.clear()
        del bpy.types.Scene.gltf_action_filter
        del bpy.types.Scene.gltf_action_filter_active


class GLTF2_filter_action(bpy.types.PropertyGroup):
    keep: bpy.props.BoolProperty(name="Keep Animation")
    action: bpy.props.PointerProperty(type=bpy.types.Action)


class GltfExportPreferences(AddonPreferences):
    bl_idname = __name__

    export_texcoords: BoolProperty(name="UVs", description="Export UVs (texture coordinates) with meshes", default=True)
    export_normals: BoolProperty(name="Normals", description="Export vertex normals with meshes", default=True)
    export_gn_mesh: BoolProperty(
        name="Geometry Nodes Instances (Experimental)",
        description="Export Geometry nodes instance meshes",
        default=False,
    )
    export_draco_mesh_compression_enable: BoolProperty(
        name="Draco Mesh Compression", description="Compress mesh using Draco", default=False
    )
    export_draco_mesh_compression_level: IntProperty(
        name="Compression Level",
        description="Compression level (0 = most speed, 6 = most compression, higher values currently not supported)",
        default=6,
        min=0,
        max=10,
    )
    export_draco_position_quantization: IntProperty(
        name="Position Quantization Bits",
        description="Quantization bits for position values (0 = no quantization)",
        default=14,
        min=0,
        max=30,
    )
    export_draco_normal_quantization: IntProperty(
        name="Normal Quantization Bits",
        description="Quantization bits for normal values (0 = no quantization)",
        default=10,
        min=0,
        max=30,
    )
    export_draco_texcoord_quantization: IntProperty(
        name="Texcoord Quantization Bits",
        description="Quantization bits for texture coordinate values (0 = no quantization)",
        default=12,
        min=0,
        max=30,
    )
    export_draco_color_quantization: IntProperty(
        name="Color Quantization Bits",
        description="Quantization bits for color values (0 = no quantization)",
        default=10,
        min=0,
        max=30,
    )
    export_draco_generic_quantization: IntProperty(
        name="Generic Quantization Bits",
        description="Quantization bits for generic values like weights or joints (0 = no quantization)",
        default=12,
        min=0,
        max=30,
    )
    export_tangents: BoolProperty(name="Tangents", description="Export vertex tangents with meshes", default=False)
    export_materials: EnumProperty(
        name="Materials",
        items=(
            ("EXPORT", "Export", "Export all materials used by included objects"),
            (
                "PLACEHOLDER",
                "Placeholder",
                "Do not export materials, but write multiple primitive groups per mesh, keeping material slot information",
            ),
            ("VIEWPORT", "Viewport", "Export minimal materials as defined in Viewport display properties"),
            (
                "NONE",
                "No export",
                "Do not export materials, and combine mesh primitive groups, losing material slot information",
            ),
        ),
        description="Export materials",
        default="EXPORT",
    )
    export_vertex_color: EnumProperty(
        name="Use Vertex Color",
        items=(
            ("MATERIAL", "Material", "Export vertex color when used by material"),
            ("ACTIVE", "Active", "Export active vertex color"),
            ("NAME", "Name", "Export vertex color with this name"),
            ("NONE", "None", "Do not export vertex color"),
        ),
        description="How to export vertex color",
        default="MATERIAL",
    )

    export_vertex_color_name: StringProperty(
        name="Vertex Color Name", description="Name of vertex color to export", default="Color"
    )

    export_all_vertex_colors: BoolProperty(
        name="Export All Vertex Colors",
        description=(
            "Export all vertex colors, even if not used by any material. "
            "If no Vertex Color is used in the mesh materials, a fake COLOR_0 will be created, "
            "in order to keep material unchanged"
        ),
        default=True,
    )

    export_active_vertex_color_when_no_material: BoolProperty(
        name="Export Active Vertex Color When No Material",
        description="When there is no material on object, export active vertex color",
        default=True,
    )
    export_yup: BoolProperty(name="+Y Up", description="Export using glTF convention, +Y up", default=True)
    export_apply: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers (excluding Armatures) to mesh objects -" "WARNING: prevents exporting shape keys",
        default=True,
    )
    export_shared_accessors: BoolProperty(
        name="Shared Accessors", description="Export Primitives using shared accessors for attributes", default=False
    )
    export_animations: BoolProperty(
        name="Animations", description="Exports active actions and NLA tracks as glTF animations", default=True
    )
    export_frame_range: BoolProperty(
        name="Limit to Playback Range", description="Clips animations to selected playback range", default=False
    )
    export_frame_step: IntProperty(
        name="Sampling Rate", description="How often to evaluate animated values (in frames)", default=1, min=1, max=120
    )
    export_force_sampling: BoolProperty(
        name="Always Sample Animations", description="Apply sampling to all animations", default=True
    )
    export_sampling_interpolation_fallback: EnumProperty(
        name="Sampling Interpolation Fallback",
        items=(
            ("LINEAR", "Linear", "Linear interpolation between keyframes"),
            ("STEP", "Step", "No interpolation between keyframes"),
        ),
        description="Interpolation fallback for sampled animations, when the property is not keyed",
        default="LINEAR",
    )
    export_pointer_animation: BoolProperty(
        name="Export Animation Pointer (Experimental)",
        description="Export material, Light & Camera animation as Animation Pointer. "
        "Available only for baked animation mode 'NLA Tracks' and 'Scene'",
        default=False,
    )
    export_animation_mode: EnumProperty(
        name="Animation Mode",
        items=(
            ("ACTIONS", "Actions", "Export actions (actives and on NLA tracks) as separate animations"),
            ("ACTIVE_ACTIONS", "Active actions merged", "All the currently assigned actions become one glTF animation"),
            (
                "BROADCAST",
                "Broadcast actions",
                "Broadcast all compatible actions to all objects. "
                "Animated objects will get all actions compatible with them, "
                "others will get no animation at all",
            ),
            ("NLA_TRACKS", "NLA Tracks", "Export individual NLA Tracks as separate animation"),
            ("SCENE", "Scene", "Export baked scene as a single animation"),
        ),
        description="Export Animation mode",
        default="ACTIONS",
    )
    export_nla_strips_merged_animation_name: StringProperty(
        name="Merged Animation Name", description=("Name of single glTF animation to be exported"), default="Animation"
    )
    export_def_bones: BoolProperty(
        name="Export Deformation Bones Only", description="Export Deformation bones only", default=False
    )
    export_hierarchy_flatten_bones: BoolProperty(
        name="Flatten Bone Hierarchy",
        description="Flatten Bone Hierarchy. Useful in case of non decomposable transformation matrix",
        default=False,
    )
    export_hierarchy_flatten_objs: BoolProperty(
        name="Flatten Object Hierarchy",
        description="Flatten Object Hierarchy. Useful in case of non decomposable transformation matrix",
        default=False,
    )
    export_armature_object_remove: BoolProperty(
        name="Remove Armature Object",
        description=(
            "Remove Armature object if possible. " "If Armature has multiple root bones, object will not be removed"
        ),
        default=False,
    )
    export_leaf_bone: BoolProperty(
        name="Add Leaf Bones",
        description=(
            "Append a final bone to the end of each chain to specify last bone length "
            "(use this when you intend to edit the armature from exported data)"
        ),
        default=False,
    )
    export_optimize_animation_size: BoolProperty(
        name="Optimize Animation Size",
        description=("Reduce exported file size by removing duplicate keyframes"),
        default=True,
    )
    export_optimize_animation_keep_anim_armature: BoolProperty(
        name="Force Keeping Channels for Bones",
        description=(
            "If all keyframes are identical in a rig, "
            "force keeping the minimal animation. "
            "When off, all possible channels for "
            "the bones will be exported, even if empty "
            "(minimal animation, 2 keyframes)"
        ),
        default=True,
    )
    export_optimize_animation_keep_anim_object: BoolProperty(
        name="Force Keeping Channel for Objects",
        description=(
            "If all keyframes are identical for object transformations, " "force keeping the minimal animation"
        ),
        default=False,
    )
    export_negative_frame: EnumProperty(
        name="Negative Frames",
        items=(
            ("SLIDE", "Slide", "Slide animation to start at frame 0"),
            ("CROP", "Crop", "Keep only frames above frame 0"),
        ),
        description="Negative Frames are slid or cropped",
        default="SLIDE",
    )
    export_anim_slide_to_zero: BoolProperty(
        name="Set All glTF Animation Starting at 0",
        description=("Set all glTF animation starting at 0.0s. " "Can be useful for looping animations"),
        default=False,
    )
    export_bake_animation: BoolProperty(
        name="Bake All Objects Animations",
        description=(
            "Force exporting animation on every object. "
            "Can be useful when using constraints or driver. "
            "Also useful when exporting only selection"
        ),
        default=False,
    )
    export_merge_animation: EnumProperty(
        name="Merge Animation",
        items=(
            ("NLA_TRACK", "NLA Track Names", "Merge by NLA Track Names"),
            ("ACTION", "Actions", "Merge by Actions"),
            ("NONE", "No Merge", "Do Not Merge Animations"),
        ),
        description="Merge Animations",
        default="ACTION",
    )
    export_anim_single_armature: BoolProperty(
        name="Export all Armature Actions",
        description=(
            "Export all actions, bound to a single armature. "
            "WARNING: Option does not support exports including multiple armatures"
        ),
        default=True,
    )
    export_reset_pose_bones: BoolProperty(
        name="Reset Pose Bones Between Actions",
        description=(
            "Reset pose bones between each action exported. "
            "This is needed when some bones are not keyed on some animations"
        ),
        default=True,
    )
    export_current_frame: BoolProperty(
        name="Use Current Frame as Object Rest Transformations",
        description=(
            "Export the scene in the current animation frame. "
            "When off, frame 0 is used as rest transformations for objects"
        ),
        default=False,
    )
    export_rest_position_armature: BoolProperty(
        name="Use Rest Position Armature",
        description=(
            "Export armatures using rest position as joints' rest pose. "
            "When off, current frame pose is used as rest pose"
        ),
        default=True,
    )
    export_anim_scene_split_object: BoolProperty(
        name="Split Animation by Object",
        description=("Export Scene as seen in Viewport, " "But split animation by Object"),
        default=True,
    )
    export_skins: BoolProperty(name="Skinning", description="Export skinning (armature) data", default=True)
    export_influence_nb: IntProperty(
        name="Bone Influences", description="Choose how many Bone influences to export", default=4, min=1
    )
    export_all_influences: BoolProperty(
        name="Include All Bone Influences",
        description="Allow export of all joint vertex influences. Models may appear incorrectly in many viewers",
        default=False,
    )
    export_morph: BoolProperty(name="Shape Keys", description="Export shape keys (morph targets)", default=True)
    export_morph_normal: BoolProperty(
        name="Shape Key Normals", description="Export vertex normals with shape keys (morph targets)", default=True
    )
    export_morph_tangent: BoolProperty(
        name="Shape Key Tangents", description="Export vertex tangents with shape keys (morph targets)", default=False
    )
    export_morph_animation: BoolProperty(
        name="Shape Key Animations", description="Export shape keys animations (morph targets)", default=True
    )
    export_morph_reset_sk_data: BoolProperty(
        name="Reset Shape Keys Between Actions",
        description=(
            "Reset shape keys between each action exported. "
            "This is needed when some SK channels are not keyed on some animations"
        ),
        default=True,
    )
    export_try_sparse_sk: BoolProperty(
        name="Use Sparse Accessor if Better", description="Try using Sparse Accessor if it saves space", default=True
    )
    export_try_omit_sparse_sk: BoolProperty(
        name="Omitting Sparse Accessor if Data is Empty",
        description="Omitting Sparse Accessor if data is empty",
        default=False,
    )
    export_gpu_instances: BoolProperty(
        name="GPU Instances",
        description="Export using EXT_mesh_gpu_instancing. "
        "Limited to children of a given Empty. "
        "Multiple materials might be omitted",
        default=False,
    )
    export_action_filter: BoolProperty(
        name="Filter Actions",
        description="Filter Actions to be exported",
        default=False,
        update=on_export_action_filter_changed,
    )
    export_convert_animation_pointer: BoolProperty(
        name="Convert TRS/Weights to Animation Pointer",
        description="Export TRS and weights as Animation Pointer. " "Using KHR_animation_pointer extension",
        default=False,
    )
    export_loglevel: IntProperty(
        name="Log Level",
        description="Log Level",
        default=-1,
    )

    def draw(self, context):
        operator = self
        layout = self.layout
        layout.use_property_split = True

        export_panel_transform(layout, operator)
        export_panel_data(layout, operator)
        export_panel_animation(layout, operator)


def export_panel_transform(layout, operator):
    header, body = layout.panel("GLTF_export_transform", default_closed=True)
    header.label(text="Transform")
    if body:
        body.prop(operator, "export_yup")


def export_panel_data(layout, operator):
    header, body = layout.panel("GLTF_export_data", default_closed=True)
    header.label(text="Data")
    if body:
        export_panel_data_scene_graph(body, operator)
        export_panel_data_mesh(body, operator)
        export_panel_data_material(body, operator)
        export_panel_data_shapekeys(body, operator)
        export_panel_data_armature(body, operator)
        export_panel_data_skinning(body, operator)


def export_panel_data_scene_graph(layout, operator):
    header, body = layout.panel("GLTF_export_data_scene_graph", default_closed=True)
    header.label(text="Scene Graph")
    if body:
        body.prop(operator, "export_gn_mesh")
        body.prop(operator, "export_gpu_instances")
        body.prop(operator, "export_hierarchy_flatten_objs")


def export_panel_data_mesh(layout, operator):
    header, body = layout.panel("GLTF_export_data_mesh", default_closed=True)
    header.label(text="Mesh")
    if body:
        body.prop(operator, "export_apply")
        body.prop(operator, "export_texcoords")
        body.prop(operator, "export_normals")
        col = body.column()
        col.active = operator.export_normals
        col.prop(operator, "export_tangents")

        col = body.column()
        col.prop(operator, "export_shared_accessors")

        header, sub_body = body.panel("GLTF_export_data_material_vertex_color", default_closed=True)
        header.label(text="Vertex Colors")
        if sub_body:
            row = sub_body.row()
            row.prop(operator, "export_vertex_color")
            row = sub_body.row()
            if operator.export_vertex_color == "NAME":
                row.prop(operator, "export_vertex_color_name")
            if operator.export_vertex_color in ["ACTIVE", "NAME"]:
                row = sub_body.row()
                row.label(
                    text="Note that fully compliant glTF 2.0 engine/viewer will use it as multiplicative factor for base color.",
                    icon="ERROR",
                )
                row = sub_body.row()
                row.label(
                    text="If you want to use VC for any other purpose than vertex color, you should use custom attributes."
                )
            row = sub_body.row()
            row.active = operator.export_vertex_color != "NONE"
            row.prop(operator, "export_all_vertex_colors")
            row = sub_body.row()
            row.active = operator.export_vertex_color != "NONE"
            row.prop(operator, "export_active_vertex_color_when_no_material")


def export_panel_data_material(layout, operator):
    header, body = layout.panel("GLTF_export_data_material", default_closed=True)
    header.label(text="Material")
    if body:
        body.prop(operator, "export_materials")
        col = body.column()
        col.active = operator.export_materials == "EXPORT"


def export_panel_data_shapekeys(layout, operator):
    header, body = layout.panel("GLTF_export_data_shapekeys", default_closed=True)
    header.use_property_split = False
    header.prop(operator, "export_morph", text="")
    header.label(text="Shape Keys")
    if body:
        body.active = operator.export_morph

        body.prop(operator, "export_morph_normal")
        col = body.column()
        col.active = operator.export_morph_normal
        col.prop(operator, "export_morph_tangent")

        # Data-Shape Keys-Optimize
        header, sub_body = body.panel("GLTF_export_data_shapekeys_optimize", default_closed=True)
        header.label(text="Optimize Shape Keys")
        if sub_body:
            row = sub_body.row()
            row.prop(operator, "export_try_sparse_sk")

            row = sub_body.row()
            row.active = operator.export_try_sparse_sk
            row.prop(operator, "export_try_omit_sparse_sk")


def export_panel_data_armature(layout, operator):
    header, body = layout.panel("GLTF_export_data_armature", default_closed=True)
    header.label(text="Armature")
    if body:
        body.active = operator.export_skins

        body.prop(operator, "export_rest_position_armature")

        row = body.row()
        row.active = operator.export_force_sampling
        row.prop(operator, "export_def_bones")
        if operator.export_force_sampling is False and operator.export_def_bones is True:
            body.label(text="Export only deformation bones is not possible when not sampling animation")
        row = body.row()
        row.prop(operator, "export_armature_object_remove")
        row = body.row()
        row.prop(operator, "export_hierarchy_flatten_bones")
        row = body.row()
        row.prop(operator, "export_leaf_bone")


def export_panel_data_skinning(layout, operator):
    header, body = layout.panel("GLTF_export_data_skinning", default_closed=True)
    header.use_property_split = False
    header.prop(operator, "export_skins", text="")
    header.label(text="Skinning")
    if body:
        body.active = operator.export_skins

        row = body.row()
        row.prop(operator, "export_influence_nb")
        row.active = not operator.export_all_influences
        body.prop(operator, "export_all_influences")


def export_panel_data_compression(layout, operator):
    header, body = layout.panel("GLTF_export_data_compression", default_closed=True)
    header.use_property_split = False
    header.prop(operator, "export_draco_mesh_compression_enable", text="")
    header.label(text="Compression")
    if body:
        body.active = operator.export_draco_mesh_compression_enable

        body.prop(operator, "export_draco_mesh_compression_level")

        col = body.column(align=True)
        col.prop(operator, "export_draco_position_quantization", text="Quantize Position")
        col.prop(operator, "export_draco_normal_quantization", text="Normal")
        col.prop(operator, "export_draco_texcoord_quantization", text="Tex Coord")
        col.prop(operator, "export_draco_color_quantization", text="Color")
        col.prop(operator, "export_draco_generic_quantization", text="Generic")


def export_panel_animation(layout, operator):
    header, body = layout.panel("GLTF_export_animation", default_closed=True)
    header.use_property_split = False
    header.prop(operator, "export_animations", text="")
    header.label(text="Animation")
    if body:
        body.active = operator.export_animations

        body.prop(operator, "export_animation_mode")
        if operator.export_animation_mode == "ACTIVE_ACTIONS":
            layout.prop(operator, "export_nla_strips_merged_animation_name")

        if operator.export_animation_mode in ["NLA_TRACKS", "SCENE"]:
            export_panel_animation_notes(body, operator)
        export_panel_animation_bake_and_merge(body, operator)
        export_panel_animation_ranges(body, operator)
        export_panel_animation_armature(body, operator)
        export_panel_animation_shapekeys(body, operator)
        export_panel_animation_sampling(body, operator)
        export_panel_animation_pointer(body, operator)
        export_panel_animation_optimize(body, operator)

        from io_scene_gltf2.blender.com.gltf2_blender_ui import export_panel_animation_action_filter

        export_panel_animation_action_filter(body, operator)


def export_panel_animation_notes(layout, operator):
    header, body = layout.panel("GLTF_export_animation_notes", default_closed=True)
    header.label(text="Notes")
    if body:
        if operator.export_animation_mode == "SCENE":
            body.label(text="Scene mode uses full bake mode:")
            body.label(text="- sampling is active")
            body.label(text="- baking all objects is active")
            body.label(text="- Using scene frame range")
        elif operator.export_animation_mode == "NLA_TRACKS":
            body.label(text="Track mode uses full bake mode:")
            body.label(text="- sampling is active")
            body.label(text="- baking all objects is active")


def export_panel_animation_bake_and_merge(layout, operator):
    header, body = layout.panel("GLTF_export_animation_bake_and_merge", default_closed=False)
    header.label(text="Bake & Merge")
    if body:
        body.active = operator.export_animations

        row = body.row()
        row.active = operator.export_force_sampling and operator.export_animation_mode in [
            "ACTIONS",
            "ACTIVE_ACTIONS",
            "BROACAST",
        ]
        row.prop(operator, "export_bake_animation")

        if operator.export_animation_mode == "SCENE":
            row = body.row()
            row.prop(operator, "export_anim_scene_split_object")

        row = body.row()
        row.active = operator.export_force_sampling and operator.export_animation_mode in ["ACTIONS"]
        row.prop(operator, "export_merge_animation")

        row = body.row()


def export_panel_animation_ranges(layout, operator):
    header, body = layout.panel("GLTF_export_animation_ranges", default_closed=True)
    header.label(text="Rest & Ranges")
    if body:
        body.active = operator.export_animations

        body.prop(operator, "export_current_frame")
        row = body.row()
        row.active = operator.export_animation_mode in ["ACTIONS", "ACTIVE_ACTIONS", "BROADCAST", "NLA_TRACKS"]
        row.prop(operator, "export_frame_range")
        body.prop(operator, "export_anim_slide_to_zero")
        row = body.row()
        row.active = operator.export_animation_mode in ["ACTIONS", "ACTIVE_ACTIONS", "BROADCAST", "NLA_TRACKS"]
        body.prop(operator, "export_negative_frame")


def export_panel_animation_armature(layout, operator):
    header, body = layout.panel("GLTF_export_animation_armature", default_closed=True)
    header.label(text="Armature")
    if body:
        body.active = operator.export_animations

        row = body.row()
        row.active = operator.export_animation_mode == "ACTIONS"
        row.prop(operator, "export_anim_single_armature")
        row = body.row()
        row.prop(operator, "export_reset_pose_bones")


def export_panel_animation_shapekeys(layout, operator):
    header, body = layout.panel("GLTF_export_animation_shapekeys", default_closed=True)
    header.active = operator.export_animations and operator.export_morph
    header.use_property_split = False
    header.prop(operator, "export_morph_animation", text="")
    header.label(text="Shape Keys Animation")
    if body:
        body.active = operator.export_animations and operator.export_morph

        row = body.row()
        row.active = operator.export_morph_animation
        row.prop(operator, "export_morph_reset_sk_data")


def export_panel_animation_sampling(layout, operator):
    header, body = layout.panel("GLTF_export_animation_sampling", default_closed=True)
    header.use_property_split = False
    header.prop(operator, "export_force_sampling", text="")
    header.label(text="Sampling Animations")
    if body:
        body.active = operator.export_animations and operator.export_force_sampling

        body.prop(operator, "export_frame_step")
        body.prop(operator, "export_sampling_interpolation_fallback")


def export_panel_animation_pointer(layout, operator):
    header, body = layout.panel("GLTF_export_animation_pointer", default_closed=True)
    header.use_property_split = False
    header.active = operator.export_animations and operator.export_animation_mode in ["NLA_TRACKS", "SCENE"]
    header.prop(operator, "export_pointer_animation", text="")
    header.label(text="Animation Pointer (Experimental)")
    if body:
        row = body.row()
        row.active = header.active and operator.export_pointer_animation
        row.prop(operator, "export_convert_animation_pointer")


def export_panel_animation_optimize(layout, operator):
    header, body = layout.panel("GLTF_export_animation_optimize", default_closed=True)
    header.label(text="Optimize Animations")
    if body:
        body.active = operator.export_animations

        body.prop(operator, "export_optimize_animation_size")

        row = body.row()
        row.prop(operator, "export_optimize_animation_keep_anim_armature")

        row = body.row()
        row.prop(operator, "export_optimize_animation_keep_anim_object")
