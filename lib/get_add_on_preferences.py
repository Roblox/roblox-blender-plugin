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

# The add-on is registered under its top-level Python package name (see RbxAddonPreferences.bl_idname = __name__
# in the root __init__.py). In Blender 4.2+/5.x, when an add-on is installed via "Install from Disk" it may be
# registered through the Extensions system, which means the registered key looks like
# "bl_ext.user_default.<folder>" rather than the folder name on disk.
#
# Deriving the lookup key from the folder name (as this file previously did) therefore breaks under the
# Extensions system: preferences.addons[<folder>] raises KeyError, save/load of the refresh_token silently
# fails, and the user is forced to log in every Blender session.
#
# Using the top-level package name from a relative import works in both cases and matches the recommended
# pattern documented at:
#   https://docs.blender.org/manual/en/latest/advanced/extensions/addons.html#user-preferences-and-package
from .. import __package__ as _base_package


def get_add_on_preferences(preferences):
    """Returns the preferences object for the add-on"""
    return preferences.addons[_base_package].preferences
