# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""SDK-standard make request action for xMatters endpoints."""

import json
import urllib.parse

import httpx
from soar_sdk.action_results import MakeRequestOutput
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import MakeRequestParams

from ..app import Asset, app
from .common import authenticated_request


def _make_request_endpoint(endpoint):
    """Allow relative xMatters paths only and reject path traversal."""
    parsed = urllib.parse.urlsplit(endpoint.strip())
    if parsed.scheme or parsed.netloc or parsed.fragment:
        raise ValueError("endpoint must be a relative xMatters API path")

    path = parsed.path or "/"
    decoded_path = path
    while True:
        fully_decoded_path = urllib.parse.unquote(decoded_path)
        if fully_decoded_path == decoded_path:
            break
        decoded_path = fully_decoded_path
    if (
        "\\" in decoded_path
        or any(
            ord(character) < 0x20 or ord(character) == 0x7F
            for character in decoded_path
        )
        or any(part.split(";", 1)[0] in {".", ".."} for part in decoded_path.split("/"))
    ):
        raise ValueError("endpoint path contains an invalid path segment")
    return urllib.parse.urlunsplit(("", "", path, parsed.query, ""))


def _make_request_headers(value):
    if not value:
        return {}
    try:
        headers = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("headers must be a JSON object") from error
    if not isinstance(headers, dict) or not all(
        isinstance(key, str) and isinstance(item, str) for key, item in headers.items()
    ):
        raise ValueError("headers must be a JSON object with string keys and values")
    return headers


def _parse_query_parameters(query_parameters):
    if not query_parameters:
        return []
    if query_parameters.lstrip().startswith("{"):
        try:
            extra = json.loads(query_parameters)
        except json.JSONDecodeError as error:
            raise ActionFailure(
                "query_parameters must be a JSON object or query string"
            ) from error
        if not isinstance(extra, dict):
            raise ActionFailure("query_parameters must be a JSON object")
        return list(extra.items())
    return urllib.parse.parse_qsl(
        query_parameters.lstrip("?"), keep_blank_values=True
    )


def _make_request_query(endpoint, query_parameters):
    parsed = urllib.parse.urlsplit(endpoint)
    endpoint_query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    extra_query = _parse_query_parameters(query_parameters)
    endpoint_keys = {key for key, _ in endpoint_query}
    parameter_keys = {key for key, _ in extra_query}
    duplicates = sorted(endpoint_keys & parameter_keys)
    if duplicates:
        duplicate_names = ", ".join(duplicates)
        raise ActionFailure(
            f"query parameter(s) {duplicate_names} are specified in both "
            "endpoint and query_parameters"
        )
    return [*endpoint_query, *extra_query]


@app.make_request()
def make_request(params: MakeRequestParams, asset: Asset) -> MakeRequestOutput:
    """Send an authenticated HTTP request to the configured xMatters host."""
    endpoint = _make_request_endpoint(params.endpoint)
    headers = _make_request_headers(params.headers)
    query = _make_request_query(endpoint, params.query_parameters)
    parsed_endpoint = urllib.parse.urlsplit(endpoint)
    endpoint_path = urllib.parse.urlunsplit(
        ("", "", parsed_endpoint.path, "", "")
    )
    timeout = params.timeout or 30.0

    request_headers = {"Content-Type": "application/json", **headers}
    with httpx.Client(
        base_url=asset.base_url.rstrip("/"),
        timeout=timeout,
        verify=params.verify_ssl,
    ) as client:
        response = authenticated_request(
            client,
            asset,
            params.http_method,
            endpoint_path,
            headers=request_headers,
            params=query,
            content=params.body,
            oauth=True,
            verify_ssl=params.verify_ssl,
            timeout=timeout,
        )

    return MakeRequestOutput(
        status_code=response.status_code,
        response_body=response.text,
    )
