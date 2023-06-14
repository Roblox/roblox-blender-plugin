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

if "bpy" in locals():
    # Imports have run before. Need to reload the imported modules
    import importlib

    if "creator_details" in locals():
        importlib.reload(creator_details)
    if "install_dependencies" in locals():
        importlib.reload(install_dependencies)

import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    CollectionProperty,
    IntProperty,
    PointerProperty,
    EnumProperty,
)
from bpy.types import PropertyGroup, ID
import traceback


class RbxStatusProperties(PropertyGroup):
    """Class representing an individual upload status indicator in the UI"""

    text: StringProperty()
    icon: StringProperty()
    target_object: PointerProperty(type=ID)  # Both Object and Collection inherit from ID


class RbxProperties(PropertyGroup):
    """Internal add-on values only kept until the end of the session. Some of these values get copied to add-on preferences for cross-session persistence."""

    def __get_creator_items(self, context):
        """Returns a generated array of enum items for the creator selection dropdown based on the data in the creators CollectionProperty"""

        def __get_list_item(index, creator):
            """Generates an enum item used for the dropdown given a creator from the creators CollectionProperty"""
            is_user_type = creator.type == "USER"
            identifier = creator.id
            name_prefix = "User" if is_user_type else "Group"
            name = f"{name_prefix} ({creator.name})"
            description = f"ID: {creator.id}"
            icon = "USER" if is_user_type else "COMMUNITY"
            return (identifier, name, description, icon, index)

        rbx = context.window_manager.rbx
        try:
            creators = rbx.creators
            if creators:
                # Generate enum items for the dropdown from the CollectionProperty values
                creator_values = creators.values()
                creator_enum_items = [
                    __get_list_item(index, creator_values[index]) for index in range(len(creator_values))
                ]
            else:
                creator_enum_items = []

            return creator_enum_items
        except Exception as exception:
            traceback.print_exception(exception)

    def __on_rbx_property_update(self, context):
        """Should be called for each property change to ensure the latest data is copied from in-session data to add-on preferences"""
        from . import creator_details

        creator_details.save_creator_details(context.window_manager, context.preferences)

    creator: EnumProperty(
        name="Upload to",
        description="Select where to upload assets",
        update=__on_rbx_property_update,
        items=__get_creator_items,
    )

    from . import creator_details, install_dependencies

    is_installing_dependencies: BoolProperty()
    is_finished_installing_dependencies: BoolProperty(
        default=install_dependencies.dependencies_public_directory.exists()
    )
    needs_restart: BoolProperty()
    is_logged_in: BoolProperty(update=__on_rbx_property_update)
    is_processing_login_or_logout: BoolProperty()
    creators: CollectionProperty(type=creator_details.RbxCreatorData)
    has_called_load_creator: BoolProperty()
    num_objects_uploading: IntProperty()
    upload_statuses: CollectionProperty(name="Upload Statuses", type=RbxStatusProperties)
