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


class GetUserParams(Params):
    identifier: str = Param(
        description="Either the Target Name or ID of the user",
        primary=True,
        cef_types=["xmatters target name", "xmatters user id"],
    )
    embed_roles: bool | None = Param(
        description="Include a list of each user's role", default=False
    )


class LinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=["/api/xm/1/sites/98084ccd-5779-41d5-b76e-7a2c6e74b257"]
    )


class DataOutput(ActionOutput):
    description: str = OutputField(
        example_values=["Has all permissions and has access to the developer tab."]
    )
    id: str = OutputField(example_values=["728a8b66-3e83-47d9-b233-5fe7774054ba"])
    name: str = OutputField(example_values=["Company Supervisor"])


class RolesOutput(ActionOutput):
    count: float = OutputField(example_values=["1"])
    data: list[DataOutput]
    total: float = OutputField(example_values=["1"])


class SiteOutput(ActionOutput):
    id: str = OutputField(example_values=["98084ccd-5779-41d5-b76e-7a2c6e74b257"])
    links: LinksOutput
    name: str = OutputField(example_values=["Default Site"])


class GetUserOutput(ActionOutput):
    lastName: str = OutputField(column_name="Last Name", example_values=["Afflac"])
    firstName: str = OutputField(column_name="First Name", example_values=["xBen"])
    id: str = OutputField(
        column_name="ID",
        cef_types=["xmatters user id"],
        example_values=["059c47aa-4951-46d7-bc68-073e73c900e6"],
    )
    targetName: str = OutputField(
        column_name="Target Name",
        cef_types=["xmatters target name"],
        example_values=["bafflac"],
    )
    status: str = OutputField(column_name="Status", example_values=["ACTIVE"])
    externallyOwned: bool = OutputField(example_values=["False", "True"])
    language: str = OutputField(example_values=["en"])
    lastLogin: str = OutputField(example_values=["2021-07-09T08:50:29.251Z"])
    licenseType: str = OutputField(example_values=["FULL_USER"])
    links: LinksOutput
    recipientType: str = OutputField(example_values=["PERSON"])
    roles: RolesOutput
    site: SiteOutput
    timezone: str = OutputField(example_values=["US/Eastern"])
    webLogin: str = OutputField(example_values=["u1GJtIPc"])
    whenCreated: str = OutputField(example_values=["2021-07-01T06:19:56.439Z"])
    whenUpdated: str = OutputField(example_values=["2021-07-09T08:50:29.253Z"])


class GetPersonSummary(ActionOutput):
    person_id: str | None = OutputField(
        example_values=["059c47aa-4951-46d7-bc68-073e73c900e6"]
    )


@app.action(
    name="get user",
    description="Get information about a user",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=GetPersonSummary,
)
def get_person(params: GetUserParams, asset: Asset, soar: SOARClient) -> GetUserOutput:
    endpoint = "/api/xm/1/people/" + urllib.parse.quote(str(params.identifier), safe="")
    query = {"embed": "roles"} if params.embed_roles else {}
    payload = xmatters_request(asset, "GET", endpoint, params=query)
    soar.set_summary(GetPersonSummary(person_id=params.identifier))
    soar.set_message("Successfully retrieved user")
    return build_output(GetUserOutput, payload)
