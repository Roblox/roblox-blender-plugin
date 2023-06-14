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


"""
    Used in Github Actions workflow to automatically update the version number of the plugin to match the tag version
"""

import re
import sys

new_version = sys.argv[1]  # v0.0.0
file_path = sys.argv[2]

new_version_line = re.sub(r"v(\d+)\.(\d+)\.(\d+)", r'"version": (\1, \2, \3),', new_version)
version_line_pattern = r'"version": \(\d+, \d+, \d+\),  # Gets updated by Github Actions. See README for info'

with open(file_path, "r") as file:
    file_data = file.read()

file_data = re.sub(version_line_pattern, new_version_line, file_data, 1)

with open(file_path, "w") as file:
    file.write(file_data)
