# Copyright © 2023 Roblox Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the “Software”), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# SPDX-License-Identifier: MIT

import bpy


def __find_wrapping_layer_collection_recursively(layer_collection, target_collection):
    """Recursively finds the LayerCollection that wraps a target collection"""
    if layer_collection.collection == target_collection:
        return layer_collection

    for nested_layer_collection in layer_collection.children:
        result = __find_wrapping_layer_collection_recursively(nested_layer_collection, target_collection)
        if result:
            return result


def __export_with_operator(scene, view_layer, target_object, operator, operator_kwargs):
    collection = None

    # If the object is not a collection, we'll need to create a temporary collection to house it for export
    is_collection = isinstance(target_object, bpy.types.Collection)
    if not is_collection:
        collection = bpy.data.collections.new("RobloxExportCollection")
        scene.collection.children.link(collection)
        collection.objects.link(target_object)
    else:
        collection = target_object

    # Identify the LayerCollection corresponding with our Collection
    layer_collection = __find_wrapping_layer_collection_recursively(
        view_layer.layer_collection, collection
    )  # Store the previous active collection so we can reset it later

    # Store the previous active collection so we can reset it later
    previous_active_layer_collection = view_layer.active_layer_collection

    # Set the current active LayerCollection to the LayerCollection corresponding with our Layer
    # This method is called synchronously on the main thread, so we do not need to worry about user
    # input interfering with this selection during export
    view_layer.active_layer_collection = layer_collection

    # Ensure cleanup happens while still passing export exceptions through
    try:
        # Because we are using the use_active_collection parameter when we export, only objects from the collection
        # specified will be exported
        operator(
            check_existing=False, use_active_collection_with_nested=True, use_active_collection=True, **operator_kwargs
        )
    finally:
        view_layer.active_layer_collection = previous_active_layer_collection
        if not is_collection:
            bpy.data.collections.remove(collection)


def export_gltf(scene, view_layer, target_object, exported_file_path, preferences):
    """Exports the given object to a GLTF (.glb) file in the given directory_path, subject to the given preferences"""
    exported_file_path = f"{exported_file_path}.glb"
    operator_kwargs = dict(
        filepath=exported_file_path,
        export_format="GLB",
        export_texcoords=preferences.export_texcoords,
        export_normals=preferences.export_normals,
        export_gn_mesh=preferences.export_gn_mesh,
        export_draco_mesh_compression_enable=preferences.export_draco_mesh_compression_enable,
        export_draco_mesh_compression_level=preferences.export_draco_mesh_compression_level,
        export_draco_position_quantization=preferences.export_draco_position_quantization,
        export_draco_normal_quantization=preferences.export_draco_normal_quantization,
        export_draco_texcoord_quantization=preferences.export_draco_texcoord_quantization,
        export_draco_color_quantization=preferences.export_draco_color_quantization,
        export_draco_generic_quantization=preferences.export_draco_generic_quantization,
        export_tangents=preferences.export_tangents,
        export_materials=preferences.export_materials,
        export_vertex_color=preferences.export_vertex_color,
        export_all_vertex_colors=preferences.export_all_vertex_colors,
        export_active_vertex_color_when_no_material=preferences.export_active_vertex_color_when_no_material,
        export_yup=preferences.export_yup,
        export_apply=preferences.export_apply,
        export_shared_accessors=preferences.export_shared_accessors,
        export_animations=preferences.export_animations,
        export_frame_range=preferences.export_frame_range,
        export_frame_step=preferences.export_frame_step,
        export_force_sampling=preferences.export_force_sampling,
        export_sampling_interpolation_fallback=preferences.export_sampling_interpolation_fallback,
        export_pointer_animation=preferences.export_pointer_animation,
        export_animation_mode=preferences.export_animation_mode,
        export_nla_strips_merged_animation_name=preferences.export_nla_strips_merged_animation_name,
        export_def_bones=preferences.export_def_bones,
        export_hierarchy_flatten_bones=preferences.export_hierarchy_flatten_bones,
        export_hierarchy_flatten_objs=preferences.export_hierarchy_flatten_objs,
        export_armature_object_remove=preferences.export_armature_object_remove,
        export_leaf_bone=preferences.export_leaf_bone,
        export_optimize_animation_size=preferences.export_optimize_animation_size,
        export_optimize_animation_keep_anim_armature=preferences.export_optimize_animation_keep_anim_armature,
        export_optimize_animation_keep_anim_object=preferences.export_optimize_animation_keep_anim_object,
        export_negative_frame=preferences.export_negative_frame,
        export_anim_slide_to_zero=preferences.export_anim_slide_to_zero,
        export_bake_animation=preferences.export_bake_animation,
        export_merge_animation=preferences.export_merge_animation,
        export_anim_single_armature=preferences.export_anim_single_armature,
        export_reset_pose_bones=preferences.export_reset_pose_bones,
        export_current_frame=preferences.export_current_frame,
        export_rest_position_armature=preferences.export_rest_position_armature,
        export_anim_scene_split_object=preferences.export_anim_scene_split_object,
        export_skins=preferences.export_skins,
        export_influence_nb=preferences.export_influence_nb,
        export_all_influences=preferences.export_all_influences,
        export_morph=preferences.export_morph,
        export_morph_normal=preferences.export_morph_normal,
        export_morph_tangent=preferences.export_morph_tangent,
        export_morph_animation=preferences.export_morph_animation,
        export_morph_reset_sk_data=preferences.export_morph_reset_sk_data,
        export_try_sparse_sk=preferences.export_try_sparse_sk,
        export_try_omit_sparse_sk=preferences.export_try_omit_sparse_sk,
        export_gpu_instances=preferences.export_gpu_instances,
        export_action_filter=preferences.export_action_filter,
        export_convert_animation_pointer=preferences.export_convert_animation_pointer,
        export_loglevel=preferences.export_loglevel,
        filter_glob="*.glb",
    )
    __export_with_operator(scene, view_layer, target_object, bpy.ops.export_scene.gltf, operator_kwargs)
    return exported_file_path
