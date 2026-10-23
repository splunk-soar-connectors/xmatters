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
import urllib.parse

from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.params import Param, Params

from ..app import Asset, app
from .common import build_output, xmatters_request


class GetEventParams(Params):
    event_id: str = Param(
        description="Event ID", primary=True, cef_types=["xmatters event id"]
    )
    embed_recipients: bool | None = Param(description="Embed Recipients", default=False)
    embed_response_options: bool | None = Param(
        description="Embed Response Options", default=False
    )
    targeted: bool | None = Param(
        description="Return directly targeted recipients", default=False
    )


class FormOutput(ActionOutput):
    id: str = OutputField(
        cef_types=["xmatters form uuid"],
        example_values=["507e9c83-472e-4510-9655-d6764574b322"],
    )
    name: str = OutputField(example_values=["Existing incident"])


class LinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=["/api/xm/1/people/0b34a572-52d7-4c2c-b6a8-af5a84365ee4"]
    )


class PlanOutput(ActionOutput):
    id: str = OutputField(example_values=["e2a78834-6a2d-4d08-aa45-9fd20b185f50"])
    integrationConfigType: str = OutputField(example_values=["INCIDENT_MANAGEMENT"])
    name: str = OutputField(example_values=["xMatters Incident Management Workflow"])


class SiteOutput(ActionOutput):
    id: str = OutputField(example_values=["98084ccd-5779-41d5-b76e-7a2c6e74b257"])
    links: LinksOutput
    name: str = OutputField(example_values=["Default Site"])


class ResponseOptionOutput(ActionOutput):
    action: str = OutputField(example_values=["STOP_NOTIFYING_TARGET"])
    allowComments: bool
    contribution: str = OutputField(example_values=["POSITIVE"])
    description: str = OutputField(
        example_values=["Engage with this incident as a resolver"]
    )
    id: str = OutputField(example_values=["94ae0b60-f841-4307-b37b-73c5639c2ef3"])
    joinConference: bool = OutputField(example_values=[False, True])
    number: float = OutputField(example_values=[1])
    order: float = OutputField(example_values=[0])
    prompt: str = OutputField(example_values=["Accept"])
    redirectUrl: str
    text: str = OutputField(example_values=["Accept"])


class RecipientOutput(ActionOutput):
    externallyOwned: bool = OutputField(example_values=[False, True])
    firstName: str = OutputField(example_values=["xChanning"])
    id: str = OutputField(example_values=["95d73d26-f83e-4678-9c21-6c2b6c5a18e1"])
    language: str = OutputField(example_values=["en"])
    lastName: str = OutputField(example_values=["Datem"])
    links: LinksOutput
    recipientType: str = OutputField(example_values=["PERSON"])
    site: SiteOutput
    status: str = OutputField(example_values=["ACTIVE"])
    targetName: str = OutputField(
        cef_types=["xmatters target name"], example_values=["cdatem"]
    )
    targeted: bool = OutputField(example_values=[True, False])
    timezone: str = OutputField(example_values=["US/Eastern"])
    webLogin: str = OutputField(example_values=["rFS77u2l"])


class RecipientsOutput(ActionOutput):
    count: float = OutputField(example_values=["2"])
    data: list[RecipientOutput]
    links: LinksOutput
    total: float = OutputField(example_values=["2"])


class ResponseoptionsOutput(ActionOutput):
    count: float = OutputField(example_values=[2])
    data: list[ResponseOptionOutput]
    total: float = OutputField(example_values=[2])


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


class VoicemailoptionsOutput(ActionOutput):
    every: float = OutputField(example_values=[60])
    leave: str = OutputField(example_values=["callbackonly"])
    retry: float = OutputField(example_values=[0])


class GetEventOutput(ActionOutput):
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
    expirationInMinutes: float = OutputField(example_values=["1440"])
    floodControl: bool = OutputField(example_values=[False, True])
    form: FormOutput
    id: str = OutputField(
        cef_types=["xmatters event id"],
        example_values=["3f48d1f6-a897-4132-9272-f2bc945adb68"],
    )
    links: LinksOutput
    name: str = OutputField(example_values=["Incident: : "])
    notificationAuditCount: float = OutputField(example_values=["8"])
    overrideDeviceRestrictions: bool = OutputField(example_values=["False", "True"])
    plan: PlanOutput
    recipients: RecipientsOutput
    requirePhonePassword: bool = OutputField(example_values=["False", "True"])
    responseCountsEnabled: bool = OutputField(example_values=[False, True])
    responseOptions: ResponseoptionsOutput
    submitter: SubmitterOutput
    terminated: str = OutputField(example_values=["2017-06-12T18:55:55.502+0000"])
    voicemailOptions: VoicemailoptionsOutput


class GetEventSummary(ActionOutput):
    event_id: str | None = OutputField(
        example_values=["3f48d1f6-a897-4132-9272-f2bc945adb68"]
    )


@app.action(
    description="Get information about a single event",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=GetEventSummary,
)
def get_event(params: GetEventParams, asset: Asset, soar: SOARClient) -> GetEventOutput:
    """Retrieve an xMatters event, optionally embedding recipients and responses."""
    event_id = urllib.parse.quote(str(params.event_id), safe="")
    embed = []
    query = {}
    if params.embed_recipients:
        embed.append("recipients")
        query["targeted"] = bool(params.targeted)
    if params.embed_response_options:
        embed.append("responseOptions")
    if embed:
        query["embed"] = ",".join(embed)

    payload = xmatters_request(
        asset,
        "GET",
        f"/api/xm/1/events/{event_id}",
        params=query,
    )
    soar.set_summary(GetEventSummary(event_id=params.event_id))
    soar.set_message("Successfully retrieved event")
    return build_output(GetEventOutput, payload)
