# Copyright © 2023 Roblox Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# SPDX-License-Identifier: MIT

import sys
from pathlib import Path

# Get the directory path of the current script
add_on_directory = Path(__file__).parent

# Append the dependencies directories to the path so we can access the bundled python modules
# If dependencies_public doesn't exist yet, the user is prompted to install them before using the plugin
sys.path.append(str(add_on_directory / "dependencies_private"))
sys.path.append(str(add_on_directory / "dependencies_public"))

if "bpy" in locals():
    # Imports have run before. Need to reload the imported modules
    import importlib

    if "event_loop" in locals():
        importlib.reload(event_loop)
    if "status_indicators" in locals():
        importlib.reload(status_indicators)
    if "roblox_properties" in locals():
        importlib.reload(roblox_properties)
    if "oauth2_login_operators" in locals():
        importlib.reload(oauth2_login_operators)
    if "RBX_OT_upload" in locals():
        importlib.reload(RBX_OT_upload)
    if "RbxOAuth2Client" in locals():
        importlib.reload(RbxOAuth2Client)
    if "get_selected_objects" in locals():
        importlib.reload(get_selected_objects)
    if "constants" in locals():
        importlib.reload(constants)
    if "creator_details" in locals():
        importlib.reload(creator_details)
    if "RBX_OT_install_dependencies" in locals():
        importlib.reload(RBX_OT_install_dependencies)
    if "export_properties" in locals():
        importlib.reload(export_properties)
    if "export_panel_transform" in locals():
        importlib.reload(export_panel_transform)
    if "export_panel_data" in locals():
        importlib.reload(export_panel_data)
    if "export_panel_animation" in locals():
        importlib.reload(export_panel_animation)
    if "GltfExportPreferences" in locals():
        importlib.reload(GltfExportPreferences)
    if "GLTF2_filter_action" in locals():
        importlib.reload(GLTF2_filter_action)

import bpy
from bpy.app.handlers import persistent
from bpy.types import Panel
from bpy.props import StringProperty, PointerProperty, IntProperty

import traceback

bl_info = {
    "name": "Upload to Roblox",
    "author": "Roblox",
    "description": "Uses Roblox's Open Cloud API to upload selected assets from Blender to Roblox",
    "blender": (3, 2, 0),
    "version": (0, 0, 0),  # Gets updated by Github Actions. See README for info
    "location": "View3D",
    "warning": "",
    "category": "Import-Export",
}


required_version = bl_info.get("blender")
is_blender_version_supported = bpy.app.version >= required_version


from gltf_export_preferences import GltfExportPreferences


class RbxAddonPreferences(GltfExportPreferences):
    """AddOnPreferences that are serialized between Blender sessions"""

    bl_idname = __name__
    refresh_token: StringProperty()
    selected_creator_enum_index: IntProperty()

    def draw(self, context):
        GltfExportPreferences.draw(self, context)


class RBX_PT_sidebar:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Roblox"


class RBX_PT_main(RBX_PT_sidebar, Panel):
    """The Add-on UI rendered in the 3D viewport"""

    bl_idname = "RBX_PT_main"
    bl_label = "Upload to Roblox"

    def draw(self, context):
        layout = self.layout
        if not is_blender_version_supported:
            layout.row().label(text="Please update Blender!", icon="ERROR")
            layout.row().label(
                text=f"Required: Blender {'.'.join(str(v) for v in required_version)} or newer",
                icon="DOT",
            )
            layout.row().label(text=f"Your version: Blender {bpy.app.version_string}", icon="X")
            return

        from .lib import install_dependencies

        rbx = context.window_manager.rbx
        if not rbx.is_finished_installing_dependencies:
            layout.row().label(
                text=f"This plugin requires installation of dependencies the first time it is run.",
                icon="INFO",
            )

            layout.row().operator(
                install_dependencies.RBX_OT_install_dependencies.bl_idname,
                text="Installing..." if rbx.is_installing_dependencies else "Install Dependencies",
            )
            return

        if rbx.needs_restart:
            layout.row().label(text="Installation complete!", icon="CHECKMARK")
            layout.row().label(text="Restart Blender to continue.")
            return

        # Blender does not provide an API for us to hook into to read the creator details when
        # the plugin loads. Instead, we will fetch this information on the first draw of the
        # main panel
        if not rbx.has_called_load_creator:
            from .lib import creator_details

            creator_details.load_creator_details(context.window_manager, context.preferences)

        if not rbx.is_logged_in:
            from .lib import oauth2_login_operators

            button_text = "Logging in..." if rbx.is_processing_login_or_logout else "Log in"
            layout.row().operator(oauth2_login_operators.RBX_OT_oauth2_login.bl_idname, text=button_text)

            # This cancel button renders for logins requiring the browser, but not for automatic logins via refreshing a remembered token
            if bpy.ops.rbx.oauth2_cancel_login.poll():
                layout.row().operator(oauth2_login_operators.RBX_OT_oauth2_cancel_login.bl_idname)


class RBX_PT_creator(RBX_PT_sidebar, Panel):
    bl_parent_id = "RBX_PT_main"
    bl_label = "Creator"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        rbx = context.window_manager.rbx
        layout = self.layout
        top_row = layout.row()

        if rbx.is_logged_in:
            try:
                from .lib.oauth2_client import RbxOAuth2Client

                oauth2_client = RbxOAuth2Client(rbx)
                top_row.label(text=f"Hello, {oauth2_client.name}")
            except Exception as exception:
                self.report({"ERROR"}, f"{str(exception)}\n{traceback.format_exc()}")

        from .lib import oauth2_login_operators

        button_text = "Working..." if rbx.is_processing_login_or_logout else "Log out"
        top_row.operator(oauth2_login_operators.RBX_OT_oauth2_logout.bl_idname, text=button_text)

        if not rbx.is_processing_login_or_logout:
            layout.prop(rbx, "creator")

    @classmethod
    def poll(cls, context):
        rbx = context.window_manager.rbx
        return rbx.is_logged_in


class RBX_PT_upload(RBX_PT_sidebar, Panel):
    bl_parent_id = "RBX_PT_main"
    bl_label = "Upload"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        from .lib.upload_operator import RBX_OT_upload

        layout = self.layout
        layout.row().operator(RBX_OT_upload.bl_idname)

        from .lib.get_selected_objects import get_selected_objects

        selected_text = ", ".join(obj.name for obj in get_selected_objects(context))
        if selected_text:
            layout.row().label(text="Selected Objects", icon="RESTRICT_SELECT_OFF")
            layout.box().label(text=selected_text)

        from .lib import status_indicators

        status_indicators.draw_statuses(context.window_manager, layout)

    @classmethod
    def poll(cls, context):
        rbx = context.window_manager.rbx
        return rbx.is_logged_in and not rbx.is_processing_login_or_logout


@persistent
def load_post(dummy):
    from .lib import event_loop

    event_loop.reset_timer_running()


def get_classes():
    if not is_blender_version_supported:
        return (RBX_PT_main,)

    from .lib import (
        event_loop,
        creator_details,
        oauth2_login_operators,
        roblox_properties,
    )
    from .lib.install_dependencies import RBX_OT_install_dependencies
    from .lib.upload_operator import RBX_OT_upload
    from gltf_export_preferences import GLTF2_filter_action

    return (
        event_loop.RBX_OT_event_loop,
        RBX_OT_install_dependencies,
        creator_details.RbxCreatorData,
        oauth2_login_operators.RBX_OT_oauth2_login,
        oauth2_login_operators.RBX_OT_oauth2_cancel_login,
        oauth2_login_operators.RBX_OT_oauth2_logout,
        RBX_PT_main,
        RBX_PT_creator,
        RBX_OT_upload,
        RBX_PT_upload,
        roblox_properties.RbxStatusProperties,
        roblox_properties.RbxProperties,
        GLTF2_filter_action,
        RbxAddonPreferences,
    )


def register():
    for cls in get_classes():
        bpy.utils.register_class(cls)

    if is_blender_version_supported:
        from .lib import roblox_properties

        bpy.types.WindowManager.rbx = PointerProperty(type=roblox_properties.RbxProperties)
        bpy.app.handlers.load_post.append(load_post)


def unregister():
    # We unregister in reverse order to ensure a class is not unregistered while
    # another still depends on it
    for cls in reversed(get_classes()):
        bpy.utils.unregister_class(cls)

    if is_blender_version_supported:
        del bpy.types.WindowManager.rbx
        bpy.app.handlers.load_post.remove(load_post)
