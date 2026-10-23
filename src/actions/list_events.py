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
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.params import Param, Params
from ..app import Asset, app
from .common import build_output, page_endpoint, xmatters_request


class ListEventsParams(Params):
    property_name: str | None = Param(
        description="Comma-separated list of property names"
    )
    property_value: str | None = Param(
        description="Comma-separated list of property values"
    )
    offset: float | None = Param(
        description="Number of items to skip before returning results"
    )
    limit: float | None = Param(description="The number of items to return")
    status: str | None = Param(
        description="Status of the event",
        value_list=["", "ACTIVE", "SUSPENDED", "TERMINATED"],
    )
    from_: str | None = Param(
        default=None,
        required=False,
        description="A date in UTC Format for the start of a time range to search",
        alias="from",
    )
    to: str | None = Param(
        description="A date in UTC Format for the end of a time range to search"
    )
    page_uri: str | None = Param(description="URI For the page")


class FormOutput(ActionOutput):
    id: str = OutputField(example_values=["a1e9d1f2-7e9e-4ea5-8ab1-a33788a07dd7"])
    name: str = OutputField(example_values=["New Incident Notification"])


class LinksOutput(ActionOutput):
    self: str = OutputField(example_values=["/api/xm/1/events?offset=0&limit=100"])


class PlanOutput(ActionOutput):
    id: str = OutputField(example_values=["e2a78834-6a2d-4d08-aa45-9fd20b185f50"])
    integrationConfigType: str = OutputField(example_values=["INCIDENT_MANAGEMENT"])
    name: str = OutputField(example_values=["xMatters Incident Management Workflow"])


class RelatedincidentOutput(ActionOutput):
    id: str = OutputField(example_values=["b7050f6b-d6a3-4c9b-8c82-83a66d4cf296"])
    links: LinksOutput


class SubmitterOutput(ActionOutput):
    firstName: str = OutputField(example_values=["test_user"])
    id: str = OutputField(
        cef_types=["xmatters user id"],
        example_values=["0b34a572-52d7-4c2c-b6a8-af5a84365ee4"],
    )
    lastName: str = OutputField(example_values=["Edwards"])
    links: LinksOutput
    recipientType: str = OutputField(example_values=["PERSON"])
    targetName: str = OutputField(
        cef_types=["xmatters target name"], example_values=["test_user"]
    )


class DataOutput(ActionOutput):
    incident: str = OutputField(
        column_name="Incident", example_values=["INCIDENT_ID-2094001"]
    )
    eventId: str = OutputField(
        column_name="Event ID",
        cef_types=["xmatters event id"],
        example_values=["2094001"],
    )
    status: str = OutputField(column_name="Status", example_values=["TERMINATED"])
    priority: str = OutputField(column_name="Priority", example_values=["LOW"])
    created: str = OutputField(
        column_name="Created", example_values=["2017-06-12T18:55:21.291+0000"]
    )
    bypassPhoneIntro: bool = OutputField(example_values=["False", "True"])
    escalationOverride: bool = OutputField(example_values=["False", "True"])
    eventType: str = OutputField(example_values=["USER"])
    floodControl: bool = OutputField(example_values=[False, True])
    form: FormOutput
    id: str = OutputField(
        cef_types=["xmatters event id"],
        example_values=["3f48d1f6-a897-4132-9272-f2bc945adb68"],
    )
    links: LinksOutput
    name: str = OutputField(example_values=["Incident: INC-1: Testing"])
    overrideDeviceRestrictions: bool = OutputField(example_values=["False", "True"])
    plan: PlanOutput
    relatedIncident: RelatedincidentOutput
    requestId: str = OutputField(
        example_values=["0bbbb7f2-e24c-43b7-ba45-49e20a1189a8"]
    )
    requirePhonePassword: bool = OutputField(example_values=["False", "True"])
    responseCountsEnabled: bool = OutputField(example_values=[False, True])
    submitter: SubmitterOutput
    terminated: str = OutputField(example_values=["2017-06-12T18:55:55.502+0000"])


class ListEventsOutput(ActionOutput):
    count: float = OutputField(example_values=[5])
    data: list[DataOutput]
    links: LinksOutput
    total: float = OutputField(example_values=["5"])


class ListEventsSummary(ActionOutput):
    events_returned: float | None = OutputField(example_values=[5])
    next_page: str | None = OutputField(
        example_values=["/api/xm/1/events?offset=4&limit=4"]
    )


@app.action(
    description="Query for specific events by providing a property name/value",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=ListEventsSummary,
)
def list_events(
    params: ListEventsParams, asset: Asset, soar: SOARClient
) -> ListEventsOutput:
    endpoint = "/api/xm/1/events"
    if params.page_uri:
        endpoint = page_endpoint(asset, params.page_uri, endpoint)
        query = None
    else:
        query = {}
        if params.property_name is not None:
            query["propertyName"] = params.property_name
        if params.property_value is not None:
            query["propertyValue"] = params.property_value
        if params.offset is not None:
            query["offset"] = params.offset
        if params.limit is not None:
            query["limit"] = params.limit
        if params.status:
            query["status"] = params.status
        if params.from_ is not None:
            query["from"] = params.from_
        if params.to is not None:
            query["to"] = params.to
    payload = xmatters_request(asset, "GET", endpoint, params=query)
    links = payload.get("links") or {}
    soar.set_summary(
        ListEventsSummary(
            events_returned=payload.get("count"), next_page=links.get("next")
        )
    )
    soar.set_message("Events retrieved successfully")
    return build_output(ListEventsOutput, payload)
