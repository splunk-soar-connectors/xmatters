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
from .common import build_output, xmatters_request


class UpdateEventParams(Params):
    event_id: str = Param(
        description="Event ID", primary=True, cef_types=["xmatters event id"]
    )
    status: str = Param(
        description="Status of the event",
        value_list=["ACTIVE", "SUSPENDED", "TERMINATED"],
    )


class FormOutput(ActionOutput):
    id: str = OutputField(example_values=["507e9c83-472e-4510-9655-d6764574b322"])


class LinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=["/api/xm/1/people/0b34a572-52d7-4c2c-b6a8-af5a84365ee4"]
    )


class SiteOutput(ActionOutput):
    id: str = OutputField(example_values=["98084ccd-5779-41d5-b76e-7a2c6e74b257"])
    links: LinksOutput
    name: str = OutputField(example_values=["Default Site"])


class ResponseOptionOutput(ActionOutput):
    action: str = OutputField(example_values=["END"])
    contribution: str = OutputField(example_values=["POSITIVE"])
    description: str = OutputField(example_values=["Acknowledge to own this task"])
    joinConference: bool = OutputField(example_values=["False", "True"])
    number: float = OutputField(example_values=["1"])
    prompt: str = OutputField(example_values=["Acknowledge to own this task"])
    text: str = OutputField(example_values=["Acknowledge"])


class RecipientOutput(ActionOutput):
    externallyOwned: bool = OutputField(example_values=["False", "True"])
    firstName: str = OutputField(example_values=["xBen"])
    id: str = OutputField(example_values=["059c47aa-4951-46d7-bc68-073e73c900e6"])
    language: str = OutputField(example_values=["en"])
    lastName: str = OutputField(example_values=["Afflac"])
    links: LinksOutput
    recipientType: str = OutputField(example_values=["PERSON"])
    site: SiteOutput
    status: str = OutputField(example_values=["ACTIVE"])
    targetName: str = OutputField(
        cef_types=["xmatters target name"], example_values=["bafflac"]
    )
    targeted: bool = OutputField(example_values=[True, False])
    timezone: str = OutputField(example_values=["US/Eastern"])
    webLogin: str = OutputField(example_values=["u1GJtIPc"])


class RecipientsOutput(ActionOutput):
    count: float = OutputField(example_values=["1"])
    data: list[RecipientOutput]
    links: LinksOutput
    total: float = OutputField(example_values=["1"])


class ResponseoptionsOutput(ActionOutput):
    count: float = OutputField(example_values=["2"])
    data: list[ResponseOptionOutput]
    total: float = OutputField(example_values=["2"])


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


class UpdateEventOutput(ActionOutput):
    incident: str = OutputField(
        column_name="Incident", example_values=["INCIDENT_ID-2132003"]
    )
    eventId: str = OutputField(
        column_name="Event ID",
        cef_types=["xmatters event id"],
        example_values=["2132003"],
    )
    status: str = OutputField(
        column_name="Updated Status", example_values=["SUSPENDED"]
    )
    bypassPhoneIntro: bool = OutputField(example_values=["False", "True"])
    created: str = OutputField(example_values=["2017-06-12T20:49:46.860+0000"])
    escalationOverride: bool = OutputField(example_values=["False", "True"])
    eventType: str = OutputField(example_values=["USER"])
    expirationInMinutes: float = OutputField(example_values=["1440"])
    floodControl: bool = OutputField(example_values=[False, True])
    form: FormOutput
    id: str = OutputField(example_values=["e2c792c3-c5d5-430d-a109-0fbae07807fe"])
    links: LinksOutput
    notificationAuditCount: float = OutputField(example_values=["4"])
    overrideDeviceRestrictions: bool = OutputField(example_values=["False", "True"])
    priority: str = OutputField(example_values=["MEDIUM"])
    recipients: RecipientsOutput
    requirePhonePassword: bool = OutputField(example_values=["False", "True"])
    responseOptions: ResponseoptionsOutput
    submitter: SubmitterOutput


class UpdateEventSummary(ActionOutput):
    event_id: str | None = OutputField(
        example_values=["3f48d1f6-a897-4132-9272-f2bc945adb68"]
    )


@app.action(
    description="Update the status of an event",
    action_type="generic",
    read_only=False,
    render_as="table",
    summary_type=UpdateEventSummary,
)
def update_event(
    params: UpdateEventParams, asset: Asset, soar: SOARClient
) -> UpdateEventOutput:
    payload = xmatters_request(
        asset,
        "POST",
        "/api/xm/1/events",
        json_body={"id": params.event_id, "status": params.status},
    )
    soar.set_summary(UpdateEventSummary(event_id=params.event_id))
    soar.set_message("Successfully updated event")
    return build_output(UpdateEventOutput, payload)
