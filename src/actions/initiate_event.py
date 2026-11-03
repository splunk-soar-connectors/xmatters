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
import json
import urllib.parse
from soar_sdk.abstract import SOARClient
from soar_sdk.action_results import ActionOutput, OutputField
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params
from ..app import Asset, app
from .common import build_output, xmatters_request


class CreateEventParams(Params):
    form_uuid: str = Param(
        description="The Form UUID", primary=True, cef_types=["xmatters form uuid"]
    )
    recipients: str = Param(description="Comma-separated list of user names")
    properties: str | None = Param(
        description="A JSON object of property names and values"
    )
    callbacks: str | None = Param(
        description="The list of Event Update Callback Objects"
    )
    priority: str | None = Param(
        description="The priority of the event",
        value_list=["", "LOW", "MEDIUM", "HIGH"],
    )
    conferences: str | None = Param(description="The list of conferences bridges")
    responses: str | None = Param(description="A JSON list of response option UUIDs")


class CreateEventOutput(ActionOutput):
    id: str = OutputField(
        column_name="New Event ID",
        cef_types=["xmatters event id"],
        example_values=["2132004"],
    )


class CreateEventSummary(ActionOutput):
    event_id: str | None = OutputField(example_values=["2132004"])


@app.action(
    name="create event",
    description="Create (trigger) an event in xMatters",
    action_type="generic",
    read_only=False,
    render_as="table",
    summary_type=CreateEventSummary,
    verbose='See <a href=\\"https://help.xmatters.com/OnDemand/xmodwelcome/communicationplanbuilder/appendixrestapi.htm?cshid=apiPOSTtrigger#POSTtrigger\\">this link</a> for more information on the parameters. The input expects the actual string literal representations of their respective fields. Lists need to be enclosed in square braces, objects in curly braces, etc.',
)
def initiate_event(
    params: CreateEventParams, asset: Asset, soar: SOARClient
) -> CreateEventOutput:
    """Create an xMatters event using the legacy trigger endpoint."""
    endpoint = (
        "/reapi/2015-04-01/forms/"
        + urllib.parse.quote(str(params.form_uuid), safe="")
        + "/triggers"
    )
    body = {
        "recipients": [
            {"targetName": target.strip()} for target in params.recipients.split(",")
        ]
    }
    for name in ("properties", "callbacks", "conferences", "responses"):
        value = getattr(params, name)
        if value is not None:
            try:
                body[name] = json.loads(value)
            except (TypeError, json.JSONDecodeError) as exc:
                raise ActionFailure(
                    f"Unable to parse parameter '{name}' as JSON"
                ) from exc
    if params.priority is not None:
        body["priority"] = params.priority

    payload = xmatters_request(asset, "POST", endpoint, json_body=body, oauth=False)
    soar.set_summary(CreateEventSummary(event_id=payload.get("id")))
    soar.set_message("Event created successfully")
    return build_output(CreateEventOutput, payload)
