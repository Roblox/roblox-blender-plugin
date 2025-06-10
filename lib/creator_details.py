# Copyright © 2025 Roblox Corporation

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

"""Functions handling the loading and saving of session creator configuration to Add-on preferences"""

if "bpy" in locals():
    # Imports have run before. Need to reload the imported modules
    import importlib

    if "get_add_on_preferences" in locals():
        importlib.reload(get_add_on_preferences)
    if "RbxOAuth2Client" in locals():
        importlib.reload(RbxOAuth2Client)

import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, EnumProperty

# The properties from the rbx object that are to be loaded from / saved to Add-on preferences
SAVED_PROPERTY_NAMES = [
    "selected_creator_enum_index",
    "refresh_token",
]


class RbxCreatorData(PropertyGroup):
    """Stores info about a creator that the user can upload to"""

    id: StringProperty(name="ID")
    type: EnumProperty(
        name="Type",
        items=[
            ("USER", "User", "Upload to your account", "USER", 0),
            ("GROUP", "Group", "Upload to a group", "COMMUNITY", 1),
        ],
        default="USER",
    )
    name: StringProperty(name="Name")


def get_selected_creator_data(window_manager):
    """Returns the RbxCreatorData object in the CollectionProperty corresponding with the current creator ID selected
    in the EnumProperty dropdown."""
    rbx = window_manager.rbx
    creator_data = next(
        (creator_data for creator_data in rbx.creators if creator_data.id == rbx.creator),
        None,
    )
    return creator_data


def save_creator_details(window_manager, preferences):
    """Applies the creator details configured in the active session to the add-on
    preferences so they persist between sessions
    """
    from .get_add_on_preferences import get_add_on_preferences

    add_on_preferences = get_add_on_preferences(preferences)
    rbx = window_manager.rbx

    for property_name in SAVED_PROPERTY_NAMES:
        match property_name:
            case "refresh_token":
                from .oauth2_client import RbxOAuth2Client

                oauth2client = RbxOAuth2Client(rbx)
                value = oauth2client.token_data.get(property_name)
            case "selected_creator_enum_index":
                # Reading an EnumProperty with . gives the identifier. Reading it with [] or .get() gives the enum index.
                # Setting a Blender RNA property with . triggers the updated event callbacks. Setting it with [] does not.
                # Later, when loading these properties, we need to avoid triggering updated events until all properties are loaded,
                # so it uses brackets to set properties. This means for EnumProperties, it is setting it by enum index rather than identifier.
                # So, we use .get() here to save the enum index. This also applies to any other enums we save.
                value = rbx.get("creator")
            case _:
                value = rbx.get(property_name)

        if value:
            add_on_preferences[property_name] = value
        else:
            add_on_preferences.property_unset(property_name)

    # Force user preferences to save. This saves preferences for all add-ons which is not ideal,
    # but is the best workaround we have for now to ensure these details save on close
    preferences.use_preferences_save = True


def load_creator_details(window_manager, preferences):
    """Applies the creator details saved in the add-on preferences to the active session"""
    rbx = window_manager.rbx
    rbx.has_called_load_creator = True

    from .get_add_on_preferences import get_add_on_preferences

    add_on_preferences = get_add_on_preferences(preferences)

    for property_name in SAVED_PROPERTY_NAMES:
        property_holder = rbx
        property_to_set = property_name
        match property_name:
            case "refresh_token":
                from .oauth2_client import RbxOAuth2Client

                oauth2client = RbxOAuth2Client(rbx)
                property_holder = oauth2client.token_data
            case "selected_creator_enum_index":
                property_to_set = "creator"

        # Referencing with brackets to avoid triggering the update function & saving over the rest of the properties with non-loaded data
        property_holder[property_to_set] = add_on_preferences.get(property_name)
