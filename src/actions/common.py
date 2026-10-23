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
from soar_sdk.action_results import PermissiveActionOutput
from soar_sdk.auth import (
    BasicAuth,
    OAuthBearerAuth,
    OAuthClientError,
    OAuthConfig,
    OAuthToken,
    SOARAssetOAuthClient,
)
from soar_sdk.exceptions import ActionFailure

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
    try:
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
    except httpx.HTTPError as error:
        raise ActionFailure(
            "Could not complete the xMatters OAuth token request."
        ) from error

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        details = _safe_vendor_error_details(response, asset)
        raise ActionFailure(
            "xMatters OAuth token request failed with HTTP "
            f"{response.status_code}{details}"
        ) from error

    try:
        token_payload = response.json()
    except (TypeError, ValueError) as error:
        raise ActionFailure(
            "The xMatters OAuth token endpoint returned invalid JSON."
        ) from error

    try:
        token = OAuthToken.model_validate(token_payload)
    except (TypeError, ValueError) as error:
        raise ActionFailure(
            "The xMatters OAuth token endpoint returned an invalid token payload."
        ) from error

    # Persist in the SDK OAuthState shape so the SDK client can own expiry and
    # refresh-token handling on subsequent requests.
    oauth_state = asset.auth_state.get_all()
    oauth_data = oauth_state.get("oauth") or {}
    if not isinstance(oauth_data, dict):
        oauth_data = {}
    oauth_data["token"] = token.model_dump(mode="json", exclude_none=True)
    oauth_data["client_id"] = asset.client_id
    oauth_state["oauth"] = oauth_data
    asset.auth_state.put_all(oauth_state)


def _build_sdk_oauth_bearer_auth(asset, client, *, verify_ssl=True, timeout=30.0):
    """Create SDK bearer auth; token retrieval and refresh stay SDK-managed."""
    oauth_client = _oauth_client(asset, client, verify_ssl=verify_ssl, timeout=timeout)
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
    if any(header.lower() == "authorization" for header in request_headers):
        raise ActionFailure(
            "Authorization headers are not accepted; configure authentication on the xMatters asset."
        )

    if asset.client_id and oauth:
        auth = _build_sdk_oauth_bearer_auth(
            asset, client, verify_ssl=verify_ssl, timeout=timeout
        )
        try:
            response = client.request(
                method,
                endpoint,
                headers=request_headers,
                auth=auth,
                **request_kwargs,
            )
        except OAuthClientError:
            oauth_client = _oauth_client(
                asset,
                client,
                verify_ssl=verify_ssl,
                timeout=timeout,
            )
            _fetch_password_grant(asset, client, oauth_client)
            auth = OAuthBearerAuth(oauth_client)
            try:
                return client.request(
                    method,
                    endpoint,
                    headers=request_headers,
                    auth=auth,
                    **request_kwargs,
                )
            except OAuthClientError as retry_error:
                raise ActionFailure(
                    "xMatters OAuth authentication failed after password-grant fallback."
                ) from retry_error

        # OAuthBearerAuth already refreshes and retries a 401 when possible.
        # A remaining 401 gets at most one xMatters password-grant retry.
        if response.status_code == 401:
            oauth_client = _oauth_client(
                asset, client, verify_ssl=verify_ssl, timeout=timeout
            )
            _fetch_password_grant(asset, client, oauth_client)
            auth = OAuthBearerAuth(oauth_client)
            try:
                return client.request(
                    method,
                    endpoint,
                    headers=request_headers,
                    auth=auth,
                    **request_kwargs,
                )
            except OAuthClientError as error:
                raise ActionFailure(
                    "xMatters OAuth authentication failed after password-grant fallback."
                ) from error
        return response

    auth = BasicAuth(asset.username, asset.password)
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


def normalize_csv_filter(value):
    """Trim and remove empty values from comma-separated API filters."""
    items = [item.strip() for item in value.split(",")]
    normalized = [item for item in items if item]
    return ",".join(normalized) if normalized else None


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


def _safe_vendor_error_details(response, asset):
    """Extract safe, structured xMatters error fields without exposing secrets."""
    try:
        payload = response.json()
    except (TypeError, ValueError):
        return ""
    if not isinstance(payload, dict):
        return ""

    sensitive_values = [
        getattr(asset, field, None)
        for field in ("username", "password", "client_id", "client_secret")
    ]
    try:
        oauth_state = asset.auth_state.get_all().get("oauth") or {}
        token = oauth_state.get("token") if isinstance(oauth_state, dict) else None
        if isinstance(token, dict):
            sensitive_values.extend(
                token.get(field) for field in ("access_token", "refresh_token")
            )
    except (AttributeError, TypeError):
        pass

    details = []
    for field in (
        "code",
        "reason",
        "subcode",
        "message",
        "error",
        "error_description",
    ):
        value = payload.get(field)
        if not isinstance(value, str | int | float):
            continue
        value = str(value)
        for secret in sensitive_values:
            if isinstance(secret, str) and secret:
                value = value.replace(secret, "[REDACTED]")
        details.append(f"{field}: {value}")

    return f" ({'; '.join(details)})" if details else ""


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
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            details = _safe_vendor_error_details(response, asset)
            raise ActionFailure(
                f"xMatters API request failed with HTTP {response.status_code}{details}"
            ) from error
        if not response.content:
            return {}
        return response.json()


def build_output(_model, payload):
    """Preserve undeclared API fields in SDK-serializable action outputs."""
    if isinstance(payload, list):
        return [PermissiveActionOutput(**item) for item in payload]
    return PermissiveActionOutput(**payload)
