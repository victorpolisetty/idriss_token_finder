# ------------------------------------------------------------------------------
#
#   Copyright 2024 victorpolisetty
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains a scaffold of a handler."""

import json
import re
from urllib.parse import unquote, urlparse

from aea.skills.base import Handler
import requests
from packages.eightballer.protocols.http.message import HttpMessage as ApiHttpMessage


class ApiHttpHandler(Handler):
    """Implements the API HTTP handler."""

    SUPPORTED_PROTOCOL = ApiHttpMessage.protocol_id  # type: Optional[str]

    def setup(self) -> None:
        """Set up the handler."""

    def teardown(self) -> None:
        """Tear down the handler."""

    def handle(self, message: ApiHttpMessage) -> None:
        """Handle incoming API HTTP messages."""
        method = message.method.lower()
        parsed_url = urlparse(unquote(message.url))
        path = parsed_url.path
        body = message.body

        self.context.logger.info(f"Received {method.upper()} request for {path}")

        normalized_path = path.rstrip("/")

        handler_name, kwargs = self.get_handler_name_and_kwargs(method, normalized_path, path, body)

        handler_method = getattr(self, handler_name, None)

        if handler_method:
            self.context.logger.debug(f"Found handler method: {handler_name}")
            return handler_method(message, **kwargs)
        self.context.logger.warning(f"No handler found for {method.upper()} request to {path}")
        return self.handle_unexpected_message(message)

    def get_handler_name_and_kwargs(self, method: str, normalized_path: str, body: bytes) -> tuple[str, dict]:
        """Get the handler name and kwargs for the given method and path."""
        handler_name = f"handle_{method}_{normalized_path.lstrip('/').replace('/', '_')}"

        kwargs = {"body": body} if method in {"post", "put", "patch"} else {}
        return handler_name, kwargs



    def handle_post_api_analyze(self, message: ApiHttpMessage, body):
        """Handle POST request for /api/analyze."""
        self.context.logger.debug(f"Request body: {body}")
        
        try:
            # Parse the incoming request body
            request_data = json.loads(body.decode("utf-8"))
            query = request_data.get("query")
            max_results = request_data.get("max_results", 25)
            page = request_data.get("page", 0)
            
            if not query:
                raise ValueError("Query parameter is required.")
            
            # Define the Searchcaster API endpoint
            searchcaster_endpoint = "https://searchcaster.xyz/api/search"
            
            # Construct the request parameters
            params = {
                "text": query,
                "count": max_results,
                "page": page,
            }
            
            # Make the HTTP request to Searchcaster
            response = requests.get(searchcaster_endpoint, params=params)
            response.raise_for_status()
            
            # Parse the response from Searchcaster
            results = response.json()
            
            # Prepare the response body
            response_body = {
                "results": [
                    {
                        "post_id": cast.get("merkleRoot"),
                        "text": cast["body"]["data"]["text"],
                        "username": cast["body"]["username"],
                        "displayName": cast["meta"]["displayName"],
                        "engagement": {
                            "reactions": cast["meta"]["reactions"]["count"],
                            "recasts": cast["meta"]["recasts"]["count"],
                            "watches": cast["meta"]["watches"]["count"]
                        },
                        "tags": cast["meta"].get("tags", []),
                        "mentions": cast["meta"].get("mentions", [])
                    }
                    for cast in results.get("casts", [])
                ]
            }
            
            # Return the formatted response
            return ApiHttpMessage(
                performative=ApiHttpMessage.Performative.RESPONSE,
                status_code=200,
                status_text="OK",
                headers="Content-Type: application/json",
                version=message.version,
                body=json.dumps(response_body).encode("utf-8")
            )
        except ValueError as e:
            self.context.logger.error(f"Error processing request: {str(e)}")
            return ApiHttpMessage(
                performative=ApiHttpMessage.Performative.RESPONSE,
                status_code=400,
                status_text="Bad Request",
                headers="Content-Type: application/json",
                version=message.version,
                body=json.dumps({"error": str(e)}).encode("utf-8")
            )
        except Exception as e:
            self.context.logger.error(f"Unexpected error: {str(e)}")
            return ApiHttpMessage(
                performative=ApiHttpMessage.Performative.RESPONSE,
                status_code=500,
                status_text="Internal Server Error",
                headers="Content-Type: application/json",
                version=message.version,
                body=json.dumps({"error": "An internal error occurred"}).encode("utf-8")
            )


    def handle_post_api_transaction_payload(self, message: ApiHttpMessage, body):
        """Handle POST request for /api/transaction-payload."""
        self.context.logger.debug(f"Request body: {body}")

        # TODO: Implement POST logic for /api/transaction-payload
        # TODO: Use this template to return a response with a status code and status text
        # return ApiHttpMessage(
        #     performative=ApiHttpMessage.Performative.RESPONSE,
        #     status_code=status_code,
        #     status_text=status_text,
        #     headers="",
        #     version=message.version,
        #     body=b""
        # )
        raise NotImplementedError


    def handle_post_api_notifications(self, message: ApiHttpMessage, body):
        """Handle POST request for /api/notifications."""
        self.context.logger.debug(f"Request body: {body}")

        # TODO: Implement POST logic for /api/notifications
        # TODO: Use this template to return a response with a status code and status text
        # return ApiHttpMessage(
        #     performative=ApiHttpMessage.Performative.RESPONSE,
        #     status_code=status_code,
        #     status_text=status_text,
        #     headers="",
        #     version=message.version,
        #     body=b""
        # )
        raise NotImplementedError

    def handle_unexpected_message(self, message):
        """Handler for unexpected messages."""
        self.context.logger.info(f"Received unexpected message: {message}")
