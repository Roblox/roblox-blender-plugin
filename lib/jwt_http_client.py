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

    if "create_http_client" in locals():
        importlib.reload(create_http_client)

import bpy
from pyjwt_key_fetcher.http_client import HTTPClient
from pyjwt_key_fetcher.errors import JWTHTTPFetchError
from json import JSONDecodeError
import aiohttp


# This class is used specifically for the JWT AsyncKeyFetcher which requires a custom "get_json" method
# on its HTTPClient class. We extend the base class here with a copied implementation of get_json from
# the DefaultHTTPClient, with one modification where we create the HttpClient using certifi SSL context.
# This ensures the request has the right SSL certificate on all platforms, consistent with the rest of the codebase.
class JWTHTTPClient(HTTPClient):
    """
    A client for JWT AsyncKeyFetcher implemented using aiohttp that uses certifi SSL context.
    """

    async def get_json(self, url: str):
        """
        Get and parse JSON data from a URL.

        :param url: The URL to fetch the data from.
        :return: The JSON data as a dictionary.
        :raise JWTHTTPFetchError: If there's a problem fetching or decoding the data.
        """
        if not url.startswith("https://"):
            raise JWTHTTPFetchError("Unsupported protocol in 'iss'")

        try:
            from .create_http_client import create_http_client

            async with create_http_client() as session:
                async with session.get(url) as response:
                    try:
                        response_data = await response.json()  # Raises json.JSONDecodeError
                        response.raise_for_status()  # Raises ClientResponseError or other ClientError
                        return response_data
                    except aiohttp.ClientResponseError as exception:
                        error_description = response_data.get("error_description", None)
                        if error_description:
                            exception.message = error_description
                        raise JWTHTTPFetchError(
                            f"Failed to fetch or decode {url}:\n{error_description or str(exception)}"
                        ) from exception
        except (aiohttp.ClientError, JSONDecodeError) as e:
            raise JWTHTTPFetchError(f"Failed to fetch or decode {url}:\n{str(e)}") from e
