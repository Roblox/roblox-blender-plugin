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

    if "event_loop" in locals():
        importlib.reload(event_loop)


import bpy
from bpy.types import Operator

import sys
import subprocess
import os
import ensurepip
from pathlib import Path
import traceback
import asyncio

# Get the project root directory path
project_root_dir = Path(__file__).parent.parent

# Set the path to the dependencies_public directory
dependencies_public_directory = project_root_dir / "dependencies_public"


class RBX_OT_install_dependencies(Operator):
    """Operator for installing public dependencies for the add-on"""

    bl_idname = "rbx.install_dependencies"
    bl_label = "Install Dependencies"
    bl_description = "Installs add-on dependencies in the background"

    def execute(self, context):
        from . import event_loop

        rbx = context.window_manager.rbx

        def on_install_finished(task):
            try:
                rbx.is_installing_dependencies = False
                task.result()
                rbx.is_finished_installing_dependencies = True
                rbx.needs_restart = True
            except Exception as exception:
                dependencies_public_directory.rmdir()
                traceback.print_exception(exception)

        rbx.is_installing_dependencies = True
        event_loop.submit(self.install_dependencies(), on_install_finished)
        return {"FINISHED"}

    async def install_dependencies(self):
        dependencies_public_directory.mkdir(exist_ok=True)

        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
        except subprocess.CalledProcessError:
            ensurepip.bootstrap()
            os.environ.pop("PIP_REQ_TRACKER", None)

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(project_root_dir / "requirements.txt"),
            "--target",
            str(dependencies_public_directory),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for the installation process to complete
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"INSTALLATION OUTPUT:\n{stdout.decode()}")
        if stderr:
            print(f"DEPENDENCY INSTALLATION ERROR:\n{stderr.decode()}")

    @classmethod
    def poll(cls, context):
        rbx = context.window_manager.rbx
        return not (rbx.is_finished_installing_dependencies or rbx.is_installing_dependencies)
