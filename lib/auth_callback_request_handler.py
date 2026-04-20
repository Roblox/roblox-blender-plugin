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

    if "aiohttp" in locals():
        importlib.reload(aiohttp)
    if "web" in locals():
        importlib.reload(web)
    if "create_http_client" in locals():
        importlib.reload(create_http_client)
    if "request_login_details" in locals():
        importlib.reload(request_login_details)
    if "constants" in locals():
        importlib.reload(constants)

import bpy
import asyncio
import json
import urllib
import logging


class StateMismatchError(Exception):
    """
    Raised when the state parameter returned did not match the state sent with the authentication request.
    """


class MissingAuthCodeError(Exception):
    """
    Raised when the server did not return an authentication code.
    """


class AuthCallbackRequestHandler:
    """
    The request handler class for our server.
    """

    def __init__(self, rbx, state, code_verifier):
        self.rbx = rbx
        self.state = state
        self.code_verifier = code_verifier

        self.request_handled_event = asyncio.Event()

    # Returns an http response for the browser
    async def handle_request(self, request):
        """
        Handles the redirect back to the local server from the auth provider containing the auth code.
        Uses the auth code to request tokens, and then goes through login steps using those tokens.
        When finished, this fires an event to signal completion which also contains any exception that
        occurred during handling.

        Returns an http response viewable in the browser with any login error details, or a success message.
        """
        event = self.request_handled_event

        import aiohttp

        try:
            # Read and validate query parameters from return url
            # Raises StateMismatchError or MissingAuthCodeError
            query_params = self.__get_query_params(request)
            self.__validate_query_params(query_params)

            # Use auth code to fetch tokens
            # Raises ClientResponseError, ClientError, or JSONDecodeError
            token_data = await self.__request_tokens(query_params.get("code"))

            # Raises ClientResponseError, ClientError, JSONDecodeError, or jwt.exceptions.DecodeError
            from .request_login_details import request_login_details

            event.login_details = await request_login_details(token_data)

            # Tell the user via browser that all the login steps succeeded
            return self.__get_success_response()
        except StateMismatchError as exception:
            event.exception = exception
            logging.info("State parameter mismatch during authentication: %s", exception)
            return self.__get_error_response(
                401,
                "Error: State parameter mismatch.",
            )
        except MissingAuthCodeError as exception:
            event.exception = exception
            logging.exception("Missing authentication code during login.")
            return self.__get_error_response(
                500,
                "Error: No authentication code received.",
            )
        except json.JSONDecodeError as exception:
            event.exception = exception
            logging.exception("Server response was not valid JSON during login.")
            return self.__get_error_response(
                500,
                "Error: Server's response was not valid JSON.",
            )
        except aiohttp.ClientResponseError as exception:
            event.exception = exception
            logging.exception("Login request failed with a server response error.")
            return self.__get_error_response(
                exception.status,
                "Error: Login request failed due to a server error.",
            )
        except aiohttp.ClientError as exception:
            event.exception = exception
            logging.exception("Login request failed due to a client or network error.")
            return self.__get_error_response(
                500,
                "Error: Login request failed due to a network error.",
            )
        except Exception as exception:
            event.exception = exception
            logging.exception("Internal client error during login.")
            return self.__get_error_response(
                500,
                "Internal client error.",
            )
        finally:
            # Fire the event to let the login function resume
            event.set()

    def __get_query_params(self, request):
        """
        Parses the query parameters sent by the provider and returns the desired parameters required for the authentication process.
        """
        all_params = urllib.parse.parse_qs(request.query_string)
        desired_keys = [
            "code",
            "state",
            "error",
            "error_description",
        ]

        # parse_qs supports multiple values for a single parameter name, but we only expect and care about
        # one value for each parameter name, so we get the first in the list if it's present
        # (e.g. "error" and "error_description" are not present unless "code" is not present)
        filtered_params = {key: all_params[key][0] for key in desired_keys if key in all_params}
        return filtered_params

    def __validate_query_params(self, query_params):
        """
        Validates the query parameters received from the provider. Raises a StateMismatchError if the returned state
        parameter doesn't match with the expected state and raises a MissingAuthCodeError if the server doesn't return
        an authentication code or if the code is not present in the query parameters.
        """
        expected_state = self.state
        returned_state = query_params.get("state")
        if returned_state != expected_state:
            # Potential CSRF attack
            raise StateMismatchError(f"Returned state: {returned_state}\nExpected state: {expected_state}")

        error = query_params.get("error")
        if error:
            raise MissingAuthCodeError(query_params.get("error_description"))

        code = query_params.get("code")
        if not code:
            raise MissingAuthCodeError("Missing code in query parameters")

    async def __request_tokens(self, auth_code):
        """
        Requests the access token from the provider using the auth code received. Raises aiohttp.ClientResponseError,
        aiohttp.ClientError, or json.JSONDecodeError if any errors occur. Returns the response data in JSON format.
        """
        from . import constants

        access_token_request_data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": constants.CLIENT_ID,
            "code_verifier": self.code_verifier,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        from .create_http_client import create_http_client

        async with create_http_client() as session:
            async with session.post(
                constants.ACCESS_TOKEN_ENDPOINT,
                headers=headers,
                data=access_token_request_data,
            ) as response:
                import aiohttp

                try:
                    response_data = await response.json()  # Raises json.JSONDecodeError
                    response.raise_for_status()  # Raises ClientResponseError or other ClientError
                    return response_data
                except aiohttp.ClientResponseError as exception:
                    error_description = response_data.get(
                        "error_description",
                        None,
                    )
                    if error_description:
                        exception.message = error_description
                    raise exception

    def __get_success_response(self):
        """
        Returns a success response to the browser after successful authentication.
        """
        import aiohttp
        import aiohttp.web as web

        return web.Response(
            text="Authorization complete. You can close this window.",
            status=200,
            content_type="text/plain",
            charset="utf-8",
        )

    def __get_error_response(self, error_code, message):
        """
        Returns an error response to the browser if any errors occur during the authentication process.
        """
        import aiohttp
        import aiohttp.web as web

        return web.Response(
            text=message,
            status=error_code,
            content_type="text/plain",
        )
