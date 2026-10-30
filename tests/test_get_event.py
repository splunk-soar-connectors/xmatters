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
from typing import ClassVar

from soar_sdk.auth import OAuthBearerAuth

from src import app as app_module
from src.actions import get_event as get_event_module


class FakeSoar:
    def set_summary(self, _summary):
        pass

    def set_message(self, _message):
        pass


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self.payload = payload or {
            "id": "evt/1",
            "eventId": "evt/1",
            "status": "ACTIVE",
        }
        self.status_code = status_code
        self.is_error = status_code >= 400
        self.content = b"{}"

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeClient:
    instances: ClassVar[list] = []

    def __init__(self, *, base_url, timeout):
        self.base_url = base_url
        self.timeout = timeout
        self.calls = []
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def get(self, endpoint, *, headers, auth=None, **kwargs):
        self.calls.append((endpoint, kwargs, headers, auth))
        return FakeResponse()

    def post(self, endpoint, *, headers, data=None, json=None, **kwargs):
        self.calls.append((endpoint, {"data": data, "json": json}, headers, None))
        if data is not None:
            return FakeResponse({"access_token": "mock-token", "expires_in": 3600})
        return FakeResponse({"id": "evt/1", "eventId": "evt/1", "status": "ACTIVE"})

    def request(self, method, endpoint, *, headers, auth=None, **kwargs):
        self.calls.append((endpoint, {"method": method, **kwargs}, headers, auth))
        return FakeResponse()


class FakeBackend:
    def load_state(self):
        return {}


class FakeState:
    def __init__(self):
        self.data = {}
        self.backend = FakeBackend()

    def get_all(self):
        return self.data.copy()

    def put_all(self, data):
        self.data = data.copy()


def test_get_event_basic_auth_and_no_embed(monkeypatch):
    FakeClient.instances.clear()
    monkeypatch.setattr("httpx.Client", FakeClient)
    asset = app_module.Asset(
        base_url="https://tenant.xmatters.com/",
        username="user",
        password="pass",  # pragma: allowlist secret
    )

    result = get_event_module.get_event.__wrapped__(
        get_event_module.GetEventParams(event_id="evt/1"), asset, FakeSoar()
    )

    endpoint, _kwargs, headers, auth = FakeClient.instances[-1].calls[0]
    assert endpoint == "/api/xm/1/events/evt%2F1"
    assert headers == {"Content-Type": "application/json"}
    assert auth is not None
    assert result.eventId == "evt/1"


def test_get_event_embeds_requested_resources(monkeypatch):
    FakeClient.instances.clear()
    monkeypatch.setattr("httpx.Client", FakeClient)
    asset = app_module.Asset(
        base_url="https://tenant.xmatters.com", username="user", password="pass"
    )

    get_event_module.get_event.__wrapped__(
        get_event_module.GetEventParams(
            event_id="evt-2",
            embed_recipients=True,
            embed_response_options=True,
            targeted=True,
        ),
        asset,
        FakeSoar(),
    )

    endpoint, _kwargs, _headers, _auth = FakeClient.instances[-1].calls[0]
    assert (
        endpoint
        == "/api/xm/1/events/evt-2?targeted=True&embed=recipients,responseOptions"
    )


def test_get_event_uses_sdk_oauth_state_for_password_grant(monkeypatch):
    FakeClient.instances.clear()
    monkeypatch.setattr("httpx.Client", FakeClient)
    asset = app_module.Asset(
        base_url="https://tenant.xmatters.com",
        username="user",
        password="pass",
        client_id="client",
    )
    state = FakeState()
    object.__setattr__(asset, "_auth_state", state)

    get_event_module.get_event.__wrapped__(
        get_event_module.GetEventParams(event_id="evt-3"), asset, FakeSoar()
    )

    client = FakeClient.instances[0]
    token_endpoint, token_kwargs, _token_headers, _ = client.calls[0]
    _event_endpoint, _kwargs, _event_headers, event_auth = client.calls[1]
    assert token_endpoint == "/api/xm/1/oauth2/token"
    assert token_kwargs["data"]["grant_type"] == "password"
    assert isinstance(event_auth, OAuthBearerAuth)
    assert state.data["oauth"]["token"]["access_token"] == "mock-token"
    assert state.data["oauth"]["client_id"] == "client"
