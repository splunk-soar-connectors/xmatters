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
import pytest
from soar_sdk.exceptions import ActionFailure

from src import app as app_module
from src.actions import (
    get_oncall_user,
    get_person,
    initiate_event,
    list_events,
    list_groups,
    list_people,
    make_request,
    test_connectivity,
    update_event,
)


@pytest.fixture
def asset():
    return app_module.Asset(
        base_url="https://tenant.xmatters.com", username="user", password="pass"
    )


class FakeSoar:
    def set_summary(self, _summary):
        pass

    def set_message(self, _message):
        pass


def test_connectivity_calls_limited_events_request(monkeypatch, asset):
    calls = []
    monkeypatch.setattr(
        test_connectivity,
        "xmatters_request",
        lambda *args, **kwargs: calls.append((args, kwargs)) or {},
    )
    test_connectivity.test_connectivity.__wrapped__(asset)
    assert calls[0][0][1:] == ("GET", "/api/xm/1/events")
    assert calls[0][1]["params"] == {"limit": 1}


def test_update_event_posts_status(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        update_event,
        "xmatters_request",
        lambda *args, **kwargs: calls.append((args, kwargs)) or {"id": "event-1"},
    )
    output = update_event.update_event.__wrapped__(
        update_event.UpdateEventParams(event_id="event-1", status="ACTIVE"),
        asset,
        FakeSoar(),
    )
    assert calls[0][0][1:3] == ("POST", "/api/xm/1/events")
    assert calls[0][1]["json_body"] == {"id": "event-1", "status": "ACTIVE"}
    assert output.id == "event-1"


def test_get_person_escapes_identifier_and_embeds_roles(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        get_person,
        "xmatters_request",
        lambda *args, **kwargs: calls.append((args, kwargs)) or {"id": "u/1"},
    )
    get_person.get_person.__wrapped__(
        get_person.GetUserParams(identifier="u/1", embed_roles=True), asset, FakeSoar()
    )
    assert calls[0][0][2] == "/api/xm/1/people/u%2F1"
    assert calls[0][1]["params"] == {"embed": "roles"}


def test_initiate_event_builds_legacy_trigger_body(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        initiate_event,
        "xmatters_request",
        lambda *args, **kwargs: calls.append((args, kwargs)) or {"id": "event-2"},
    )
    params = initiate_event.CreateEventParams(
        form_uuid="form/1",
        recipients=" alice, bob ",
        properties='{"ticket": "INC-1"}',
        responses='["response-1", "response-2"]',
    )
    initiate_event.initiate_event.__wrapped__(params, asset, FakeSoar())
    assert calls[0][0][2] == "/reapi/2015-04-01/forms/form%2F1/triggers"
    assert calls[0][1]["json_body"] == {
        "recipients": [{"targetName": "alice"}, {"targetName": "bob"}],
        "properties": {"ticket": "INC-1"},
        "responses": ["response-1", "response-2"],
    }


def test_list_people_builds_search_and_page_queries(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        list_people,
        "xmatters_request",
        lambda *args, **kwargs: (
            calls.append((args, kwargs)) or {"count": 0, "data": []}
        ),
    )
    params = list_people.ListUsersParams(
        search="Alice, Bob", embed_roles=True, offset=2, limit=5
    )
    list_people.list_people.__wrapped__(params, asset, FakeSoar())
    assert calls[0][1]["params"] == {
        "search": "Alice,Bob",
        "embed": "roles",
        "offset": 2,
        "limit": 5,
    }

    unsafe = list_people.ListUsersParams(
        page_uri="https://elsewhere.invalid/api/xm/1/people"
    )
    with pytest.raises(ValueError, match="configured xMatters API origin"):
        list_people.list_people.__wrapped__(unsafe, asset, FakeSoar())


def test_list_events_maps_property_filters_and_time_range(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        list_events,
        "xmatters_request",
        lambda *args, **kwargs: (
            calls.append((args, kwargs)) or {"count": 0, "data": []}
        ),
    )
    params = list_events.ListEventsParams(
        property_name="priority,,service",
        property_value="HIGH,,,, Email",
        offset=2,
        limit=10,
        **{
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-01-02T00:00:00Z",
        },
    )
    list_events.list_events.__wrapped__(params, asset, FakeSoar())
    assert calls[0][1]["params"] == {
        "propertyName": "priority,service",
        "propertyValue": "HIGH,Email",
        "offset": 2,
        "limit": 10,
        "from": "2026-01-01T00:00:00Z",
        "to": "2026-01-02T00:00:00Z",
    }


def test_list_groups_maps_embed_filters_and_rows(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        list_groups,
        "xmatters_request",
        lambda *args, **kwargs: (
            calls.append((args, kwargs)) or {"data": [{"id": "group-1"}]}
        ),
    )
    output = list_groups.list_groups.__wrapped__(
        list_groups.ListGroupsParams(search_group="Security", embed_observers=True),
        asset,
        FakeSoar(),
    )
    assert calls[0][0][2] == "/api/xm/1/groups"
    assert calls[0][1]["params"] == {"embed": "observers", "search": "Security"}
    assert [item.id for item in output] == ["group-1"]


def test_get_oncall_validates_timeframe_and_returns_rows(asset, monkeypatch):
    calls = []
    monkeypatch.setattr(
        get_oncall_user,
        "xmatters_request",
        lambda *args, **kwargs: (
            calls.append((args, kwargs))
            or {"data": [{"members": {"count": 1}, "start": "start"}]}
        ),
    )
    output = get_oncall_user.get_oncall_user.__wrapped__(
        get_oncall_user.GetOncallUserParams(
            groups="platform, security", members_per_shift=2, embed_owner=True
        ),
        asset,
        FakeSoar(),
    )
    assert calls[0][0][2] == "/api/xm/1/on-call"
    assert calls[0][1]["params"] == {
        "embed": "members.owner",
        "groups": "platform,security",
        "membersPerShift": 2,
    }
    assert output[0].start == "start"

    invalid = get_oncall_user.GetOncallUserParams(
        groups="platform", **{"from": "start"}
    )
    with pytest.raises(ActionFailure, match="both from and to"):
        get_oncall_user.get_oncall_user.__wrapped__(invalid, asset, FakeSoar())
    assert len(calls) == 1

    invalid_member_count = get_oncall_user.GetOncallUserParams(
        groups="platform", members_per_shift=0
    )
    with pytest.raises(ActionFailure, match="valid value from 1 to 100"):
        get_oncall_user.get_oncall_user.__wrapped__(
            invalid_member_count, asset, FakeSoar()
        )
    assert len(calls) == 1


def test_make_request_rejects_absolute_url_before_httpx_client(asset, monkeypatch):
    def unexpected_client(*_args, **_kwargs):
        pytest.fail("absolute endpoints must be rejected before creating a client")

    monkeypatch.setattr(make_request.httpx, "Client", unexpected_client)
    params = make_request.MakeRequestParams(
        http_method="GET", endpoint="https://example.invalid/api/xm/1/events"
    )

    with pytest.raises(
        ValueError, match="endpoint must be a relative xMatters API path"
    ):
        make_request.make_request.__wrapped__(params, asset)
