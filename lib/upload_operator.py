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

    if "get_selected_objects" in locals():
        importlib.reload(get_selected_objects)
    if "upload_blocking_issues" in locals():
        importlib.reload(upload_blocking_issues)
    if "creator_details" in locals():
        importlib.reload(creator_details)
    if "status_indicators" in locals():
        importlib.reload(status_indicators)
    if "export_fbx" in locals():
        importlib.reload(export_fbx)
    if "get_add_on_preferences" in locals():
        importlib.reload(get_add_on_preferences)
    if "RbxOAuth2Client" in locals():
        importlib.reload(RbxOAuth2Client)
    if "str_to_int" in locals():
        importlib.reload(str_to_int)
    if "constants" in locals():
        importlib.reload(constants)
    if "AssetsUploadClient" in locals():
        importlib.reload(AssetsUploadClient)
    if "AssetsCreator" in locals():
        importlib.reload(AssetsCreator)
    if "AssetType" in locals():
        importlib.reload(AssetType)
    if "openapi_client" in locals():
        importlib.reload(openapi_client)
    if "aiolimiter" in locals():
        importlib.reload(aiolimiter)
    if "extract_exception_message" in locals():
        importlib.reload(extract_exception_message)
    if "event_loop" in locals():
        importlib.reload(event_loop)

import bpy
from bpy.types import Operator

import traceback
from tempfile import TemporaryDirectory
from pathlib import Path

NO_ASSET_ID = 0


class RBX_OT_upload(Operator):
    """Operator for the action of uploading the current selection to Roblox"""

    bl_idname = "rbx.upload"
    bl_label = "Upload"
    limiter = None

    @classmethod
    def description(cls, context, _):
        from . import upload_blocking_issues
        from .get_selected_objects import get_selected_objects

        issues_blocking_upload = upload_blocking_issues.get_issues_blocking_upload(context)
        num_selected_objects = len(get_selected_objects(context))
        is_plural = num_selected_objects > 1
        default_string = f"Upload {num_selected_objects} selected object{'s' if is_plural else ''} to Roblox"
        error_string = ".\n".join(issues_blocking_upload)
        description = error_string or default_string
        return description

    @classmethod
    def poll(cls, context):
        # We only want to allow the upload operator to be invoked if no issues are blocking
        # the user from uploading
        from . import upload_blocking_issues

        can_upload = upload_blocking_issues.get_can_upload(context)
        return can_upload

    # Although async_loop provides an AsyncModalOperatorMixin object that we can leverage to
    # run this operator's execute method asynchronously, there are elements of the upload
    # process we want to run on the main thread (see comment in upload method)
    def execute(self, context):
        from . import upload_blocking_issues

        can_upload = upload_blocking_issues.get_can_upload(context)

        # Although it should not be possible to execute this operator if issues are blocking
        # uploading, we will include this check here in case such a scenario arose without
        # poll being called
        if not can_upload:
            issues_blocking_upload = upload_blocking_issues.get_issues_blocking_upload(context)
            self.report({"ERROR"}, ".\n".join(issues_blocking_upload))
            return {"CANCELLED"}

        from .get_selected_objects import get_selected_objects

        selected_objects = get_selected_objects(context)

        # Setting the num_objects_uploading value will block future uploading until the current
        # operation is complete
        rbx = context.window_manager.rbx
        rbx.num_objects_uploading = len(selected_objects)

        # Because we are starting a new upload operation, we need to clear out the statuses of the
        # previous one from the UI
        from . import status_indicators

        status_indicators.clear_statuses(context.window_manager)

        for selected_object in selected_objects:
            self.upload(
                context.window_manager,
                context.area,
                context.scene,
                context.view_layer,
                context.preferences,
                selected_object,
            )

        return {"FINISHED"}

    @classmethod
    def upload(cls, window_manager, area, scene, view_layer, preferences, target_object):
        """Exports the given object to a FBX file, and uploads it to Roblox"""

        # FBX exporting occurs on the main thread so we are not scheduling it to be run
        # asynchronously along with the upload web requests
        from . import status_indicators, constants

        try:
            from .get_add_on_preferences import get_add_on_preferences

            add_on_preferences = get_add_on_preferences(preferences)
            temporary_directory = TemporaryDirectory()
            sanitized_object_name = "".join(c for c in target_object.name if c.isalnum() or c in (' ','.','_')).rstrip()
            exported_file_path = Path(temporary_directory.name) / f"exported_{sanitized_object_name}.fbx"
            from .export_fbx import export_fbx

            export_fbx(scene, view_layer, target_object, exported_file_path, add_on_preferences)
        except Exception as exception:
            traceback.print_exception(exception)
            status_indicators.set_status(
                window_manager, area, target_object, constants.ERROR_MESSAGES["ADD_ON_ERROR"], "ERROR"
            )
            cls.upload_complete(window_manager, temporary_directory)
        else:
            status_indicators.set_status(window_manager, area, target_object, "Waiting to upload", "DECORATE")

            # Because this method is running on the main thread, we need to execute the upload process in a separate coroutine
            from .str_to_int import str_to_int

            package_id = str_to_int(target_object.get(constants.RBX_PACKAGE_ID_PROPERTY_NAME))

            coroutine = cls.upload_task(window_manager, area, target_object, exported_file_path, package_id)

            def task_complete(task):
                cls.upload_task_complete(task, window_manager, area, target_object, temporary_directory)

            from . import event_loop

            event_loop.submit(coroutine, task_complete)

    # This asynchronous method is invoked as a separate coroutine from the main thread
    @classmethod
    async def upload_task(cls, window_manager, area, target_object, file_path, package_id):
        """Uploads the given fbx file to Roblox, and yields until it has finished processing or timed out"""
        from .oauth2_client import RbxOAuth2Client
        from . import creator_details, constants

        creator_data = creator_details.get_selected_creator_data(window_manager)
        rbx = window_manager.rbx
        oauth2_client = RbxOAuth2Client(rbx)
        await oauth2_client.refresh_login_if_needed()
        access_token = oauth2_client.token_data["access_token"]

        # We are throttling the number of upload operations per minute using the async limiter we declared
        from assets_upload_client import AssetsUploadClient
        from openapi_client.models import (
            RobloxOpenCloudAssetsV1Creator as AssetsCreator,
            RobloxOpenCloudAssetsV1AssetType as AssetType,
        )

        match creator_data.type:
            case "USER":
                creator = AssetsCreator(user_id=int(creator_data.id))
            case "GROUP":
                creator = AssetsCreator(group_id=int(creator_data.id))

        if not cls.limiter:
            import aiolimiter

            cls.limiter = aiolimiter.AsyncLimiter(constants.MAX_UPLOADS_PER_MIN)
        async with cls.limiter, AssetsUploadClient(creator=creator, oauth2_token=access_token) as client:
            from . import status_indicators

            status_indicators.set_status(window_manager, area, target_object, "Uploading", "DECORATE")
            operation = await client.upload_asset_and_wait_for_done_async(
                asset_type=AssetType.MODEL,
                asset_name=target_object.name,
                asset_description=constants.ASSET_DESCRIPTION,
                file_path=file_path,
                asset_id=package_id or NO_ASSET_ID,
                upload_request_timeout_seconds=25,
            )

        return operation

    @staticmethod
    def upload_complete(window_manager, temporary_directory):
        """Decreases the num_objects_uploading counter when an upload task completes, whether successful or errored.
        This way, once all upload tasks are resolved, the upload operator can be invoked again.
        """
        temporary_directory.cleanup()
        rbx = window_manager.rbx
        rbx.num_objects_uploading = rbx.num_objects_uploading - 1

    @staticmethod
    def upload_task_complete(task, window_manager, area, target_object, temporary_directory):
        """Handles the result of a upload task, updating the status object, setting the package ID custom
        property and cleaning up from the operation."""
        from . import status_indicators, constants
        import openapi_client
        import asyncio

        try:
            operation = task.result()
            print(f"Operation path: {operation.path}")

            if operation.error:
                status_indicators.set_status(window_manager, area, target_object, operation.error.message, "ERROR")
                print(f"Upload failed, {operation.error.code}: {operation.error.message}")
            elif not operation.done:
                # Timeout while polling for upload job to finish. It may yet finish or fail, but we stopped checking.
                status_indicators.set_status(
                    window_manager, area, target_object, constants.ERROR_MESSAGES["OPERATION_TIMED_OUT"], "ERROR"
                )
            elif operation.response:
                # Success
                target_object[constants.RBX_PACKAGE_ID_PROPERTY_NAME] = str(operation.response.asset_id)

                status_indicators.set_status(
                    window_manager,
                    area,
                    target_object,
                    f"Uploaded version {operation.response.revision_id}",
                    "CHECKMARK",
                )
            else:  # No error, no response, but is done. We don't expect this to happen
                status_indicators.set_status(
                    window_manager, area, target_object, constants.ERROR_MESSAGES["INVALID_RESPONSE"], "ERROR"
                )
                print(f"Upload failed, invalid response:\n{operation}")
        except asyncio.exceptions.TimeoutError as exception:
            # Timeout while waiting for initial upload to return an operation ID. It may yet finish or fail, but we stopped waiting.
            status_indicators.set_status(
                window_manager, area, target_object, constants.ERROR_MESSAGES["UPLOAD_TIMED_OUT"], "ERROR"
            )
        except openapi_client.rest.ApiException as exception:
            traceback.print_exception(exception)
            from .extract_exception_message import extract_exception_message

            status_indicators.set_status(
                window_manager,
                area,
                target_object,
                extract_exception_message(exception),
                "ERROR",
            )
        except Exception as exception:
            traceback.print_exception(exception)
            status_indicators.set_status(
                window_manager, area, target_object, constants.ERROR_MESSAGES["ADD_ON_ERROR"], "ERROR"
            )
        finally:
            RBX_OT_upload.upload_complete(window_manager, temporary_directory)
