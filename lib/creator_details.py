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
    "selected_creator_id",
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
        try:
            match property_name:
                case "refresh_token":
                    from .oauth2_client import RbxOAuth2Client

                    oauth2client = RbxOAuth2Client(rbx)
                    value = oauth2client.token_data.get(property_name)
                case "selected_creator_id":
                    # Use attribute access to get the enum identifier string (Blender 5.0+ removed
                    # dict-style access on bpy.props-defined properties)
                    value = getattr(rbx, "creator", "")
                case _:
                    value = getattr(rbx, property_name, None)

            if value:
                setattr(add_on_preferences, property_name, value)
            else:
                add_on_preferences.property_unset(property_name)
        except Exception as exception:
            print(f"Failed to save preference '{property_name}': {exception}")

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
        value = getattr(add_on_preferences, property_name, None)
        if not value:
            continue

        match property_name:
            case "refresh_token":
                from .oauth2_client import RbxOAuth2Client

                oauth2client = RbxOAuth2Client(rbx)
                oauth2client.token_data[property_name] = value
            case "selected_creator_id":
                # Defer creator selection until after login when enum items are available.
                # Setting rbx.creator directly here would fail (no enum items yet) and would
                # trigger the update callback prematurely.
                rbx.pending_creator_id = value
