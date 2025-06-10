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

"""Functions for the management and rendering of RbxStatusProperties objects"""


def find_status(window_manager, target_object):
    """Returns the status associated with the object, if it exists"""
    statuses = window_manager.rbx.upload_statuses.values()
    for status in statuses:
        if status.target_object == target_object:
            return status
    return None


def set_status(window_manager, area, target_object, text, icon):
    """Updates the status corresponding to an object with the given text and icon.
    If a status does not exist for this object, a new one is created.
    """
    status = find_status(window_manager, target_object)
    if status == None:
        status = window_manager.rbx.upload_statuses.add()
    status.text = text
    status.target_object = target_object
    status.icon = icon

    # Redraw the UI
    area.tag_redraw()


def clear_statuses(window_manager):
    """Removes all statuses"""
    window_manager.rbx.upload_statuses.clear()


def get_status_text(status):
    """Returns the text to be rendered in the UI for the status"""
    return f"{status.target_object.name}: {status.text}"


def draw_statuses(window_manager, layout):
    rbx = window_manager.rbx

    statuses = rbx.upload_statuses.values()
    if len(statuses) == 0:
        return

    layout.row().label(text="Upload Status", icon="COPY_ID")
    box = layout.box()
    for status in rbx.upload_statuses.values():
        if not status.text:
            # CollectionProperties sometimes contain one empty object (?)
            # TODO: Investigate if this is a bug
            continue
        box.label(text=get_status_text(status), icon=status.icon)
