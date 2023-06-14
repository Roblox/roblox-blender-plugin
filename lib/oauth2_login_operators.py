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

    if "asyncio" in locals():
        importlib.reload(asyncio)
    if "event_loop" in locals():
        importlib.reload(event_loop)
    if "creator_details" in locals():
        importlib.reload(creator_details)
    if "RbxOAuth2Client" in locals():
        importlib.reload(RbxOAuth2Client)

import bpy
from bpy.types import Operator
import traceback
import asyncio

global ongoing_login_task
ongoing_login_task = None


class RBX_OT_oauth2_login(Operator):
    """Operator for logging in with OAuth2"""

    bl_idname = "rbx.oauth2login"
    bl_label = "Log in"
    bl_description = "Log in with your Roblox account using your browser"

    def execute(self, context):
        from . import event_loop
        from .oauth2_client import RbxOAuth2Client

        global ongoing_login_task

        rbx = context.window_manager.rbx
        oauth2_client = RbxOAuth2Client(rbx)

        if not rbx.has_called_load_creator:
            from . import creator_details

            creator_details.load_creator_details(context.window_manager, context.preferences)

        def on_login_complete(task):
            global ongoing_login_task
            ongoing_login_task = None

            try:
                task.result()
            except asyncio.exceptions.CancelledError:
                pass
            except Exception as exception:
                traceback.print_exception(exception)

        def on_refresh_complete(task):
            global ongoing_login_task
            ongoing_login_task = None

            # Attempted a refresh for the remembered session
            try:
                task.result()
            except asyncio.exceptions.CancelledError:
                pass
            except Exception as exception:
                # Refresh failed during initial login, invalidate old refresh token via logout and prompt login (see: logout callback)
                traceback.print_exception(exception)
                event_loop.submit(oauth2_client.logout(), on_logout_after_failed_refresh_complete)

        def on_logout_after_failed_refresh_complete(task):
            global ongoing_login_task
            # Refresh failed during initial login, so we logged out the remembered session
            # and now want to prompt login via browser
            try:
                task.result()
            except Exception as exception:
                # Tokens are still cleared for every logout call, but we'll log any exceptions here
                traceback.print_exception(exception)
            finally:
                # Prompt a new login since the refresh failed and logout is complete
                ongoing_login_task = event_loop.submit(oauth2_client.login(), on_login_complete)

        if oauth2_client.token_data.get("refresh_token"):
            # Remembered session exists. Refresh using that token
            event_loop.submit(oauth2_client.refresh_login_if_needed(), on_refresh_complete)
        else:
            # No remembered session, start a new login
            ongoing_login_task = event_loop.submit(oauth2_client.login(), on_login_complete)

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        global ongoing_login_task
        rbx = context.window_manager.rbx

        return not (rbx.is_logged_in or rbx.is_processing_login_or_logout or bool(ongoing_login_task))


class RBX_OT_oauth2_cancel_login(Operator):
    """Operator for cancelling an ongoing OAuth2 login task"""

    bl_idname = "rbx.oauth2_cancel_login"
    bl_label = "Cancel"
    bl_description = "Stop waiting for the browser to return login info"

    def execute(self, context):
        global ongoing_login_task
        ongoing_login_task.cancel()
        ongoing_login_task = None

        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        global ongoing_login_task
        return bool(ongoing_login_task)


class RBX_OT_oauth2_logout(Operator):
    """Operator for revoking an OAuth2 session"""

    bl_idname = "rbx.oauth2logout"
    bl_label = "Log out"
    bl_description = "Log out of your Roblox account"

    def execute(self, context):
        def task_complete(task):
            try:
                task.result()
            except Exception as exception:
                traceback.print_exception(exception)

        from . import event_loop
        from .oauth2_client import RbxOAuth2Client

        rbx = context.window_manager.rbx
        oauth2_client = RbxOAuth2Client(rbx)
        event_loop.submit(oauth2_client.logout(), task_complete)
        return {"FINISHED"}

    @classmethod
    def poll(cls, context):
        rbx = context.window_manager.rbx
        return rbx.is_logged_in and not rbx.is_processing_login_or_logout
