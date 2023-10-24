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

    if "certifi" in locals():
        importlib.reload(certifi)
    if "aiohttp" in locals():
        importlib.reload(aiohttp)
    if "pyjwt_key_fetcher" in locals():
        importlib.reload(pyjwt_key_fetcher)
    if "JWTHTTPClient" in locals():
        importlib.reload(JWTHTTPClient)
    if "jwt" in locals():
        importlib.reload(jwt)
    if "create_http_client" in locals():
        importlib.reload(create_http_client)
    if "constants" in locals():
        importlib.reload(constants)

import bpy
from time import time
import json
import urllib
import ssl

# To avoid making a request with an expired token,
# we always refresh up to this many seconds before the token expires
REFRESH_SECONDS_BEFORE_EXPIRY = 30


# TODO: Replace with async implementation, move to more sensible location
def fetch_data_custom_ssl_context(self):
    import certifi

    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(self.uri, context=context) as response:
        return json.load(response)


async def request_login_details(token_data):
    """Fetches authorized resources for the access token, fetches group names for each authorized group ID,
    sets the token data in state, verifies and decodes the id token and stores the username in state.
    """
    # Use access token to fetch authorized resources
    # Raises ClientResponseError, ClientError, or JSONDecodeError
    authorized_resources = await __request_authorized_resources(token_data.get("access_token"))

    # Read creator ids from resources and fetch group names for each group ID
    # Raises ClientResponseError, ClientError, or JSONDecodeError
    creator_ids = __get_creator_ids_from_resources(authorized_resources)
    group_names_by_id = await __request_group_names_for_group_ids(creator_ids["groups"])

    # Decode the ID token into profile data, fetching the matching signature from the certs API under the hood
    # Raises jwt.exceptions.DecodeError
    profile_data = await __decode_id_token(token_data.get("id_token"))

    # Raises KeyError if missing name
    name = profile_data["name"]

    token_data = {
        "refresh_after": time() + token_data["expires_in"] - REFRESH_SECONDS_BEFORE_EXPIRY,
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "id_token": token_data["id_token"],
    }

    return creator_ids, name, group_names_by_id, token_data


async def __request_authorized_resources(access_token):
    from . import constants

    authorized_resources_request_data = {
        "client_id": constants.CLIENT_ID,
        "token": access_token,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    from .create_http_client import create_http_client

    async with create_http_client() as session:
        async with session.post(
            constants.AUTHORIZED_RESOURCES_ENDPOINT,
            headers=headers,
            data=authorized_resources_request_data,
        ) as response:
            import aiohttp

            try:
                response_data = await response.json(content_type=None)  # Raises json.JSONDecodeError
                response.raise_for_status()  # Raises ClientResponseError or other ClientError
                return response_data
            except aiohttp.ClientResponseError as exception:
                error_description = response_data.get("error_description", None)
                if error_description:
                    exception.message = error_description
                raise exception


async def __decode_id_token(id_token):
    """Decodes a jwt token. Fetches the signature from the certs api and checks the token's
    contents against the signature."""

    # The token contains a kid field in its header. To get the signing key,
    # the client matches the kid of the token to key from the certs endpoint
    # containing a matching kid.
    # Raises jwt.exceptions.DecodeError
    from . import constants
    from .jwt_http_client import JWTHTTPClient
    import pyjwt_key_fetcher

    fetcher = pyjwt_key_fetcher.AsyncKeyFetcher(http_client=JWTHTTPClient(), valid_issuers=[constants.ISSUER])
    key_entry = await fetcher.get_key(id_token)

    # Throws an error if the token could not be validated with the signing key
    import jwt

    return jwt.decode(jwt=id_token, audience=constants.CLIENT_ID, leeway=180, **key_entry)


def __get_creator_ids_from_resources(authorized_resources):
    """Parses the authorized_resources object returned from the authorized resources API to extract the
    authorized user ID and group IDs, separated so they can be easily differentiated"""
    creator_ids = {
        "user": None,
        "groups": [],
    }

    try:
        resource_infos = authorized_resources["resource_infos"][0]
        owner = resource_infos["owner"]
        creator_strings = resource_infos["resources"]["creator"]["ids"]
        if not creator_strings:
            raise ValueError("No creators were authorized during login")

        for creator_string in creator_strings:
            # Creator strings come back from the authorized resources endpoint as either "U" for user
            # or "G1234567" for groups, where the numbers are the group id
            match creator_string[0]:
                case "U":  # User
                    # The creator string is just "U", so we swap it with the owner ID
                    creator_ids["user"] = owner["id"]

                case "G":  # Group
                    # Remove the "G" from the beginning of the ID
                    group_id = creator_string[1:]
                    creator_ids["groups"].append(group_id)
    except KeyError as exception:
        raise KeyError("Missing expected data from authorized resources") from exception

    return creator_ids


async def __request_group_names_for_group_ids(group_ids):
    """Makes an http GET request to fetch the names of the groups, and returns a dictionary of group names by string id"""
    if not group_ids:
        return {}

    from . import constants

    query_params = urllib.parse.urlencode({"groupIds": group_ids}, doseq=True)
    full_url = f"{constants.GROUPS_ENDPOINT}?{query_params}"
    headers = {"Accept": "application/json"}

    from .create_http_client import create_http_client

    async with create_http_client() as session:
        async with session.get(full_url, headers=headers) as response:
            import aiohttp

            try:
                response_data = await response.json(content_type=None)  # Raises json.JSONDecodeError
                response.raise_for_status()  # Raises ClientResponseError or other ClientError
                return {str(group_data["id"]): group_data["name"] for group_data in response_data["data"]}
            except aiohttp.ClientResponseError as exception:
                for error in response_data.get("errors", []):
                    exception.message += f"{error['userFacingMessage']}\n"
                raise exception
