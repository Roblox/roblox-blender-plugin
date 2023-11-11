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


def export_fbx(scene, view_layer, target_object, exported_file_path, preferences):
    """Exports the given object to a FBX file in the given directory_path, subject to the given preferences"""
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
    layer_collection = __find_wrapping_layer_collection_recursively(view_layer.layer_collection, collection)
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
        bpy.ops.export_scene.fbx(
            filepath=str(exported_file_path),
            global_scale=preferences.export_scale,
            bake_anim=preferences.bake_anim,
            bake_anim_use_all_bones = preferences.bake_anim_use_all_bones,
            bake_anim_use_nla_strips = preferences.bake_anim_use_nla_strips,
            bake_anim_use_all_actions = preferences.bake_anim_use_all_actions,
            bake_anim_force_startend_keying = preferences.bake_anim_force_startend_keying,
            bake_anim_step = preferences.bake_anim_step,
            bake_anim_simplify_factor = preferences.bake_anim_simplify_factor,
            axis_forward="-Z",
            axis_up="Y",
            path_mode="COPY",
            embed_textures=True,
            use_active_collection=True,
        )
    finally:
        # Return to the previous active LayerCollection
        view_layer.active_layer_collection = previous_active_layer_collection

        # If we had to make a temporary collection, remove it
        if not is_collection:
            bpy.data.collections.remove(collection)

    return exported_file_path
