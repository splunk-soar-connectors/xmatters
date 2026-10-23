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
from .get_person import RolesOutput, SiteOutput


class ListUsersParams(Params):
    search: str | None = Param(
        description="Search term. Will check first name, last name, web login, etc. Separate values with either space or a + sign"
    )
    embed_roles: bool | None = Param(
        description="Include a list of each users' roles", default=False
    )
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
    page_uri: str | None = Param(description="URI For the page")


class LinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=["/api/xm/1/people?search=Ben+Natalie&offset=0&limit=4"]
    )


class DataOutput(ActionOutput):
    lastName: str = OutputField(column_name="Last Name", example_values=["Afflac"])
    firstName: str = OutputField(column_name="First Name", example_values=["xBen"])
    id: str = OutputField(
        column_name="ID", example_values=["059c47aa-4951-46d7-bc68-073e73c900e6"]
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


class ListUsersOutput(ActionOutput):
    count: float = OutputField(example_values=["2"])
    data: list[DataOutput]
    links: LinksOutput
    total: float = OutputField(example_values=["2"])


class ListPeopleSummary(ActionOutput):
    people_returned: float | None = OutputField(example_values=[2])
    next_page: str | None = OutputField(
        example_values=["/api/xm/1/people?offset=4&limit=4"]
    )


@app.action(
    description="Get information about multiple users matching a property name/value",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=ListPeopleSummary,
)
def list_people(
    params: ListUsersParams, asset: Asset, soar: SOARClient
) -> ListUsersOutput:
    endpoint = "/api/xm/1/people"
    if params.page_uri:
        endpoint = page_endpoint(asset, params.page_uri, endpoint)
        query = None
    else:
        query = {}
        if params.search is not None:
            query["search"] = ",".join(x.strip() for x in params.search.split(","))
        if params.embed_roles:
            query["embed"] = "roles"
        if params.property_name is not None:
            query["propertyName"] = params.property_name
        if params.property_value is not None:
            query["propertyValue"] = params.property_value
        if params.offset is not None:
            query["offset"] = params.offset
        if params.limit is not None:
            query["limit"] = params.limit
    payload = xmatters_request(asset, "GET", endpoint, params=query)
    links = payload.get("links") or {}
    soar.set_summary(
        ListPeopleSummary(
            people_returned=payload.get("count"), next_page=links.get("next")
        )
    )
    soar.set_message("Users retrieved successfully")
    return build_output(ListUsersOutput, payload)
