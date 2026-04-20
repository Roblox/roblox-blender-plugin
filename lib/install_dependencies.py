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

import shutil
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

# File written into dependencies_public after a successful install. Records the Python major.minor version
# the dependencies were installed against, so we can detect when Blender has been upgraded to a Python
# release that the existing dependencies don't support (e.g. Blender 4.5 ships Python 3.11 but Blender 5.1
# ships Python 3.13, and aiohttp/cryptography/urllib3 wheels are Python-version specific).
PYTHON_VERSION_MARKER = dependencies_public_directory / ".python_version"


def _current_python_tag():
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def dependencies_appear_installed():
    """
    Returns True if dependencies_public exists and either has no Python version marker (legacy install,
    assume valid for backward compatibility) or the marker matches the currently running Python.
    Returns False if the directory is missing, or if the marker is present and reports a mismatched version.
    """
    if not dependencies_public_directory.exists():
        return False
    if not PYTHON_VERSION_MARKER.exists():
        # Legacy install predating this marker. Defer judgement so existing users aren't forced to reinstall
        # spuriously; the panel's runtime canary import will catch any actual incompatibility.
        return True
    return PYTHON_VERSION_MARKER.read_text().strip() == _current_python_tag()


_dependencies_importable_cache = None


def dependencies_importable():
    """
    Returns True if the most stack-fragile dependency (aiohttp, with C extensions tied to a specific Python
    version) imports successfully. Used as a runtime canary so that a stale install left over from a previous
    Blender / Python version surfaces as a clear "reinstall" prompt rather than a silent ModuleNotFoundError
    when the user clicks Log in.

    Result is cached because draw() can run many times per second; a failing import in particular is
    expensive to repeat. The cache is invalidated by invalidate_dependencies_importable_cache() after a
    fresh install completes (though a Blender restart is still required for new modules to be picked up
    on sys.path, so the cache reset is mostly cosmetic).
    """
    global _dependencies_importable_cache
    if _dependencies_importable_cache is not None:
        return _dependencies_importable_cache

    if not dependencies_public_directory.exists():
        _dependencies_importable_cache = False
        return False
    try:
        import aiohttp  # noqa: F401
        import aiohttp.web  # noqa: F401

        _dependencies_importable_cache = True
    except Exception:
        _dependencies_importable_cache = False
    return _dependencies_importable_cache


def invalidate_dependencies_importable_cache():
    global _dependencies_importable_cache
    _dependencies_importable_cache = None


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
                # task.result() raises if the install coroutine raised (e.g. pip exited non-zero), which
                # surfaces the failure to the user instead of silently marking the install as complete.
                task.result()
                rbx.is_finished_installing_dependencies = True
                rbx.needs_restart = True
                invalidate_dependencies_importable_cache()
            except Exception as exception:
                rbx.is_finished_installing_dependencies = False
                invalidate_dependencies_importable_cache()
                # Best-effort cleanup so a partially-populated dependencies_public doesn't masquerade as a
                # successful install on the next launch. Use rmtree because rmdir refuses non-empty dirs and
                # a failed pip install often leaves files behind.
                if dependencies_public_directory.exists():
                    shutil.rmtree(dependencies_public_directory, ignore_errors=True)
                traceback.print_exception(exception)

        rbx.is_installing_dependencies = True
        event_loop.submit(self.install_dependencies(), on_install_finished)
        return {"FINISHED"}

    async def install_dependencies(self):
        # Wipe any previous install before re-populating. This matters when a user is reinstalling because
        # of a Python version upgrade — leftover wheels for the old Python version would otherwise shadow
        # the freshly installed ones on sys.path.
        if dependencies_public_directory.exists():
            shutil.rmtree(dependencies_public_directory, ignore_errors=True)
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

        # Previously this function ignored process.returncode, so a failed pip install (very common on a
        # Blender Python upgrade where the pinned wheels don't exist for the new interpreter) was silently
        # treated as success. The user would then hit ModuleNotFoundError when trying to log in. Raise on
        # non-zero so on_install_finished can surface the failure.
        if process.returncode != 0:
            raise RuntimeError(
                f"pip install exited with code {process.returncode} for Python {_current_python_tag()}. "
                f"See the terminal/system console for pip output."
            )

        # Stamp the install with the current Python major.minor so a future Blender upgrade with a newer
        # Python can detect the mismatch and prompt for a clean reinstall.
        PYTHON_VERSION_MARKER.write_text(_current_python_tag() + "\n")

    @classmethod
    def poll(cls, context):
        # Allow re-running while not actively installing. install_dependencies() now wipes the directory
        # before populating it, so reinstall is safe and is the user's recovery path when an upgrade
        # makes the existing dependencies incompatible.
        rbx = context.window_manager.rbx
        return not rbx.is_installing_dependencies
