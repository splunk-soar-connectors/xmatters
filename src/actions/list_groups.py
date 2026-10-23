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


class ListGroupsParams(Params):
    search_group: str | None = Param(
        description="Search term will check in name and description of groups. Separate multiple values with either space or a + sign"
    )
    members: str | None = Param(
        description="The targetName or id of users, dynamic teams or devices that are part of a group. Separate multiple values with commma"
    )
    status: str | None = Param(
        description="Status of the group", value_list=["", "ACTIVE", "INACTIVE"]
    )
    embed_observers: bool | None = Param(
        description="Includes a list of observers for a group"
    )
    embed_supervisors: bool | None = Param(
        description="Includes a list of supervisors for a group"
    )


class LinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=[
            "/api/xm/1/groups/3c765cff-3fe3-4229-8dc4-6b41c3d701a2/supervisors?offset=0&limit=100"
        ]
    )


class SiteOutput(ActionOutput):
    id: str = OutputField(example_values=["4b05dd34-8382-4021-93cd-2ca6b977e546"])
    name: str = OutputField(example_values=["Default Site"])
    links: LinksOutput


class DataOutput(ActionOutput):
    id: str = OutputField(example_values=["c1ae941e-5742-407d-a88d-cbc4dbbc60ae"])
    name: str = OutputField(example_values=["Scenario Administrator"])
    description: str = OutputField(
        example_values=[
            "Users with the ability to add, edit, view, and remove any Scenario."
        ]
    )


class SupervisorOutput(ActionOutput):
    id: str = OutputField(example_values=["440bbb02-07ab-43ea-b524-b1db12492b1b"])
    site: SiteOutput
    links: LinksOutput
    status: str = OutputField(example_values=["ACTIVE"])
    language: str = OutputField(example_values=["en"])
    lastName: str = OutputField(example_values=["Edwards"])
    timezone: str = OutputField(example_values=["US/Pacific"])
    webLogin: str = OutputField(example_values=["test@test.com"])
    firstName: str = OutputField(example_values=["test_user"])
    lastLogin: str = OutputField(example_values=["2021-12-29T07:46:09.541Z"])
    targetName: str = OutputField(example_values=["test"])
    licenseType: str = OutputField(example_values=["FULL_USER"])
    whenCreated: str = OutputField(example_values=["2021-07-01T06:19:56.439Z"])
    whenUpdated: str = OutputField(example_values=["2021-12-29T07:46:09.543Z"])
    recipientType: str = OutputField(example_values=["PERSON"])
    externallyOwned: bool = OutputField(example_values=[False])


class SupervisorsOutput(ActionOutput):
    data: list[SupervisorOutput]
    count: float = OutputField(example_values=[1])
    links: LinksOutput
    total: float = OutputField(example_values=[1])


class ObserversOutput(ActionOutput):
    data: list[DataOutput]
    count: float = OutputField(example_values=[1])
    total: float = OutputField(example_values=[1])


class ListGroupsOutput(ActionOutput):
    id: str = OutputField(
        column_name="Group ID",
        cef_types=["xmatters group id"],
        example_values=["3c765cff-3fe3-4229-8dc4-6b41c3d701a2"],
    )
    targetName: str = OutputField(
        column_name="Group target name",
        cef_types=["xmatters group name"],
        example_values=["test"],
    )
    status: str = OutputField(column_name="Group status", example_values=["ACTIVE"])
    links: LinksOutput
    created: str = OutputField(example_values=["2021-12-16T06:39:40.560Z"])
    groupType: str = OutputField(example_values=["ON_CALL"])
    description: str = OutputField(example_values=["test"])
    supervisors: SupervisorsOutput
    observedByAll: bool = OutputField(example_values=[True])
    recipientType: str = OutputField(example_values=["GROUP"])
    allowDuplicates: bool = OutputField(example_values=[True])
    externallyOwned: bool = OutputField(example_values=[False])
    useDefaultDevices: bool = OutputField(example_values=[True])
    observers: ObserversOutput


class ListGroupsSummary(ActionOutput):
    groups_returned: float | None = OutputField(example_values=[1])


@app.action(
    description="Get information about multiple groups matching a property",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=ListGroupsSummary,
)
def list_groups(
    params: ListGroupsParams, asset: Asset, soar: SOARClient
) -> list[ListGroupsOutput]:
    query = {}
    embeds = []
    if params.embed_observers:
        embeds.append("observers")
    if params.embed_supervisors:
        embeds.append("supervisors")
    query["embed"] = ",".join(embeds)
    if params.search_group is not None:
        query["search"] = params.search_group
    if params.members is not None:
        query["members"] = params.members
    if params.status is not None:
        query["status"] = params.status

    payload = xmatters_request(asset, "GET", "/api/xm/1//groups", params=query)
    count = payload.get("count")
    soar.set_summary(ListGroupsSummary(groups_returned=count))
    soar.set_message(f"Num of groups found: {count}")
    return build_output(ListGroupsOutput, payload["data"])
