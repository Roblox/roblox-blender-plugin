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

"""Constant variable configs that are required across modules"""

RBX_PACKAGE_ID_PROPERTY_NAME = "Roblox Package ID"
ASSET_DESCRIPTION = "Uploaded from Blender"
ERROR_MESSAGES = {
    "UPLOAD_TIMED_OUT": "Upload Timed Out",
    "OPERATION_TIMED_OUT": "Operation Timed Out",
    "INVALID_RESPONSE": "Invalid Response",
    "ADD_ON_ERROR": "Add-on Error",
}
MAX_UPLOADS_PER_MIN = 25

# OAuth2 Login
ENV = "production"
RELATIVE_REDIRECT_PATH = "/oauth2/callback"
ENVIRONMENTS = {
    "production": {
        "client_id": "2787281281124556822",
        "issuer": "https://apis.roblox.com/oauth/",
        "algorithms": ["ES256"],
        "auth_code_endpoint": "https://apis.roblox.com/oauth/v1/authorize",
        "authorized_resources_endpoint": "https://apis.roblox.com/oauth/v1/token/resources",
        "access_token_endpoint": "https://apis.roblox.com/oauth/v1/token",
        "refresh_token_endpoint": "https://apis.roblox.com/oauth/v1/token",
        "revoke_token_endpoint": "https://apis.roblox.com/oauth/v1/token/revoke",
        "groups_endpoint": "https://groups.roblox.com/v2/groups",
    },
}
CLIENT_ID = ENVIRONMENTS[ENV]["client_id"]
ISSUER = ENVIRONMENTS[ENV]["issuer"]
ACCESS_TOKEN_ENDPOINT = ENVIRONMENTS[ENV]["access_token_endpoint"]
AUTHORIZED_RESOURCES_ENDPOINT = ENVIRONMENTS[ENV]["authorized_resources_endpoint"]
REFRESH_TOKEN_ENDPOINT = ENVIRONMENTS[ENV]["refresh_token_endpoint"]
AUTH_CODE_ENDPOINT = ENVIRONMENTS[ENV]["auth_code_endpoint"]
REVOKE_TOKEN_ENDPOINT = ENVIRONMENTS[ENV]["revoke_token_endpoint"]
GROUPS_ENDPOINT = ENVIRONMENTS[ENV]["groups_endpoint"]
SCOPES = [
    "openid",
    "profile",
    "asset:read",
    "asset:write",
]
