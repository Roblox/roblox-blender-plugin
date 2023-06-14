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

import bpy
import asyncio

loop = asyncio.new_event_loop()
timer_running = False


# Blender has poor support for multi threading, which means the only way to run the asyncio event loop
# is to step it in increments using a timer. Although Blender does support registering application timers
# with bpy.app.timers, creating a modal operator that invokes itself from a timer allows us to preserve the window
# context
class RBX_OT_event_loop(bpy.types.Operator):
    bl_idname = "rbx.event_loop"
    bl_label = "Registers a timer to step the event loop"
    timer = None

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        # This timer will execute this operator
        context.window_manager.modal_handler_add(self)
        self.timer = context.window_manager.event_timer_add(0.001, window=context.window)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type != "TIMER":
            return {"PASS_THROUGH"}

        # Calling stop() before run_forever() leads to a single cycle of the event loop running
        # This works because stop() actually schedules the stop command in the event loop, so it
        # will run a after the other callbacks for this cycle have completed
        # https://stackoverflow.com/questions/29868372/python-asyncio-run-event-loop-once
        loop.stop()
        loop.run_forever()

        return {"RUNNING_MODAL"}


def submit(async_coroutine, done_callback):
    task = loop.create_task(async_coroutine)
    if done_callback != None:
        task.add_done_callback(done_callback)

    __ensure_started()
    return task


def get_loop():
    __ensure_started()
    return loop


def __ensure_started():
    global timer_running

    # We only want to start the event loop once
    if timer_running == False:
        timer_running = True
        bpy.ops.rbx.event_loop()
