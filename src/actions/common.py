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
"""Shared xMatters HTTP, authentication, and paging helpers."""

import urllib.parse

import httpx
from soar_sdk.auth import (
    BasicAuth,
    OAuthBearerAuth,
    OAuthClientError,
    OAuthConfig,
    OAuthToken,
    SOARAssetOAuthClient,
)

from ..oauth_client import migrate_legacy_oauth_state


def _oauth_client(asset, client, *, verify_ssl=True, timeout=30.0):
    migrate_legacy_oauth_state(asset)
    token_endpoint = "/api/xm/1/oauth2/token"  # noqa: S105
    config = OAuthConfig(client_id=asset.client_id, token_endpoint=token_endpoint)
    return SOARAssetOAuthClient(
        config,
        asset.auth_state,
        http_client=client,
        verify_ssl=verify_ssl,
        timeout=timeout,
    )


def _fetch_password_grant(asset, client, oauth_client):
    """Use xMatters' password grant, which the SDK does not implement."""
    response = client.post(
        oauth_client.config.token_endpoint,
        data={
            "client_id": asset.client_id,
            "grant_type": "password",
            "username": asset.username,
            "password": asset.password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()

    # Persist in the SDK OAuthState shape so the SDK client can own expiry and
    # refresh-token handling on subsequent requests.
    oauth_state = asset.auth_state.get_all()
    oauth_data = oauth_state.get("oauth") or {}
    if not isinstance(oauth_data, dict):
        oauth_data = {}
    token = OAuthToken.model_validate(response.json())
    oauth_data["token"] = token.model_dump(mode="json", exclude_none=True)
    oauth_data["client_id"] = asset.client_id
    oauth_state["oauth"] = oauth_data
    asset.auth_state.put_all(oauth_state)


def _oauth_auth(asset, client, *, force_password=False, verify_ssl=True, timeout=30.0):
    oauth_client = _oauth_client(asset, client, verify_ssl=verify_ssl, timeout=timeout)
    if force_password:
        _fetch_password_grant(asset, client, oauth_client)
    else:
        try:
            oauth_client.get_valid_token()
        except OAuthClientError:
            # Password grant is xMatters-specific; use it only when there is no
            # usable SDK-managed token or SDK refresh fails.
            _fetch_password_grant(asset, client, oauth_client)
    return OAuthBearerAuth(oauth_client)


def authenticated_request(
    client,
    asset,
    method,
    endpoint,
    *,
    headers=None,
    oauth=True,
    verify_ssl=True,
    timeout=30.0,
    **request_kwargs,
):
    """Send a request with SDK auth and xMatters password-grant fallback."""
    request_headers = headers or {}
    custom_authorization = any(
        header.lower() == "authorization" for header in request_headers
    )

    if asset.client_id and oauth and not custom_authorization:
        auth = _oauth_auth(asset, client, verify_ssl=verify_ssl, timeout=timeout)
        try:
            response = client.request(
                method,
                endpoint,
                headers=request_headers,
                auth=auth,
                **request_kwargs,
            )
        except OAuthClientError:
            auth = _oauth_auth(
                asset,
                client,
                force_password=True,
                verify_ssl=verify_ssl,
                timeout=timeout,
            )
            response = client.request(
                method,
                endpoint,
                headers=request_headers,
                auth=auth,
                **request_kwargs,
            )

        if response.status_code == 401:
            auth = _oauth_auth(
                asset,
                client,
                force_password=True,
                verify_ssl=verify_ssl,
                timeout=timeout,
            )
            response = client.request(
                method,
                endpoint,
                headers=request_headers,
                auth=auth,
                **request_kwargs,
            )
        return response

    auth = (
        None
        if custom_authorization and asset.client_id and oauth
        else BasicAuth(asset.username, asset.password)
    )
    return client.request(
        method,
        endpoint,
        headers=request_headers,
        auth=auth,
        **request_kwargs,
    )


def _query_string(params):
    """Match the legacy connector's comma-preserving xMatters query encoding."""
    return (
        urllib.parse.urlencode(params)
        .replace("%2C", ",")
        .replace("%252C", "%2C")
        .replace("%20", " ")
        .replace("%2B", "+")
    )


def _with_query(endpoint, params):
    query = _query_string(params)
    return f"{endpoint}?{query}" if query else endpoint


def page_endpoint(asset, page_uri, expected_path):
    page = urllib.parse.urlsplit(page_uri)
    base = urllib.parse.urlsplit(asset.base_url)
    if (page.scheme or page.netloc) and (page.scheme, page.netloc) != (
        base.scheme,
        base.netloc,
    ):
        raise ValueError("Pagination link must use the configured xMatters API origin")
    if not page.path.startswith(expected_path) or any(
        part in (".", "..") for part in page.path.split("/")
    ):
        raise ValueError("Invalid xMatters pagination link")
    return urllib.parse.urlunsplit(("", "", page.path, page.query, ""))


def xmatters_request(
    asset, method, endpoint, *, params=None, json_body=None, oauth=True
):
    url = _with_query(endpoint, params or {})
    headers = {"Content-Type": "application/json"}
    with httpx.Client(base_url=asset.base_url.rstrip("/"), timeout=30.0) as client:
        response = authenticated_request(
            client,
            asset,
            method,
            url,
            headers=headers,
            oauth=oauth,
            json=json_body,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()


def build_output(model, payload):
    if isinstance(payload, list):
        return [model.model_construct(**item) for item in payload]
    return model.model_construct(**payload)
