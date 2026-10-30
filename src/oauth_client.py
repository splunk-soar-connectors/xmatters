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
"""Compatibility helpers for migrating legacy xMatters OAuth state."""

import json
from datetime import UTC, datetime

from soar_sdk.auth import OAuthToken
from soar_sdk.shims.phantom.encryption_helper import encryption_helper


def migrate_legacy_oauth_state(asset):
    """Migrate the legacy cached OAuth token into SDK auth state once."""
    auth_state = asset.auth_state
    current_state = auth_state.get_all()
    sdk_oauth_state = current_state.get("oauth") or {}
    if isinstance(sdk_oauth_state, dict) and sdk_oauth_state.get("token"):
        return

    legacy_state = auth_state.backend.load_state() or {}
    legacy_token = current_state.get("oauth_token") or legacy_state.get("oauth_token")
    if isinstance(legacy_token, str):
        try:
            legacy_token = json.loads(
                encryption_helper.decrypt(legacy_token, auth_state.asset_id)
            )
        except Exception:
            # If the old token cannot be decoded (for example, after an asset ID
            # change), let the normal credential flow request a fresh token.
            return

    if not isinstance(legacy_token, dict) or not legacy_token.get("access_token"):
        return

    legacy_token = dict(legacy_token)
    if "expires_at" not in legacy_token:
        retrieval_time = current_state.get("retrieval_time") or legacy_state.get(
            "retrieval_time"
        )
        try:
            retrieved = datetime.strptime(retrieval_time, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=UTC
            )
            legacy_token["expires_at"] = retrieved.timestamp() + int(
                legacy_token.get("expires_in") or 0
            )
        except (TypeError, ValueError):
            # Missing/invalid legacy expiry metadata should trigger a refresh or
            # fresh password-grant request instead of treating the token as valid.
            legacy_token["expires_at"] = 0.0

    try:
        sdk_token = OAuthToken.model_validate(legacy_token)
    except (TypeError, ValueError):
        return

    migrated_state = dict(current_state)
    sdk_oauth_state = dict(sdk_oauth_state) if isinstance(sdk_oauth_state, dict) else {}
    sdk_oauth_state["token"] = sdk_token.model_dump(mode="json", exclude_none=True)
    sdk_oauth_state["client_id"] = asset.client_id
    migrated_state["oauth"] = sdk_oauth_state
    auth_state.put_all(migrated_state)
