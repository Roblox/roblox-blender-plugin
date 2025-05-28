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

if "bpy" in locals():
    # Imports have run before. Need to reload the imported modules
    import importlib

    if "get_selected_objects" in locals():
        importlib.reload(get_selected_objects)

import bpy


def get_issues_blocking_upload(context):
    """Returns a list of strings describing issues that prevent the user from
    uploading, if present
    """
    from .get_selected_objects import get_selected_objects

    rbx = context.window_manager.rbx
    is_logged_in = rbx.is_logged_in
    is_processing_login_or_logout = rbx.is_processing_login_or_logout
    is_object_selected = len(get_selected_objects(context)) > 0

    failure_conditions = [
        (not is_logged_in, "Log in before uploading"),
        (is_processing_login_or_logout, "Wait for login or logout to finish"),
        (not is_object_selected, "Select at least one object to upload"),
        (rbx.num_objects_uploading != 0, "Wait for current upload process to finish"),
    ]

    issues_blocking_upload = [failure_reason for condition, failure_reason in failure_conditions if condition]

    return issues_blocking_upload


def get_can_upload(context):
    """Returns true if no issues are blocking the user from uploading
    their selection, otherwise returns false
    """

    issues_blocking_upload = get_issues_blocking_upload(context)

    return len(issues_blocking_upload) == 0
