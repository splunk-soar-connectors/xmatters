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
from soar_sdk.exceptions import ActionFailure
from soar_sdk.params import Param, Params
from ..app import Asset, app
from .common import build_output, xmatters_request


class GetOncallUserParams(Params):
    groups: str = Param(
        description="Name or id of a group. Separate multiple values with commma",
        primary=True,
        cef_types=["xmatters group id", "xmatters group name"],
    )
    members_per_shift: float | None = Param(
        description="The number of shift members to include (Default: 3, Max: 100)",
        default=3,
    )
    from_: str | None = Param(
        default=None,
        required=False,
        description="Date time value in UTC format (Eg. 2022-01-01T03:00:00Z)",
        alias="from",
    )
    to: str | None = Param(
        description="Date time value in UTC format (Eg. 2022-01-01T04:00:00Z)"
    )
    embed_shift: bool | None = Param(description="Includes shift details")
    embed_owner: bool | None = Param(description="Includes members owner details")


class LinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=["/api/xm/1/people/3c4edf02-ea0b-457c-bd83-766c4021ada6"]
    )


class GroupOutput(ActionOutput):
    id: str = OutputField(example_values=["ce423b4a-1ecd-48f9-a4ac-71cef75f9875"])
    links: LinksOutput
    groupType: str = OutputField(example_values=["ON_CALL"])
    targetName: str = OutputField(example_values=["Service-Team-1"])
    recipientType: str = OutputField(example_values=["GROUP"])


class EndOutput(ActionOutput):
    endBy: str = OutputField(example_values=["NEVER"])


class RecurrenceOutput(ActionOutput):
    end: EndOutput
    frequency: str = OutputField(example_values=["DAILY"])
    repeatEvery: float = OutputField(example_values=[1])


class ShiftOutput(ActionOutput):
    id: str = OutputField(example_values=["97fbe2ff-430c-4700-af24-bf076c9aaf48"])
    name: str = OutputField(example_values=["Default Shift"])
    links: LinksOutput
    end: str = OutputField(example_values=["2015-08-06T12:00:00.000Z"])
    group: GroupOutput
    start: str = OutputField(example_values=["2015-08-05T21:00:00.000Z"])
    timezone: str = OutputField(example_values=["US/Eastern"])
    recurrence: RecurrenceOutput


class SiteOutput(ActionOutput):
    id: str = OutputField(example_values=["4b05dd34-8382-4021-93cd-2ca6b977e546"])
    name: str = OutputField(example_values=["Default Site"])
    links: LinksOutput


class OwnerOutput(ActionOutput):
    id: str = OutputField(example_values=["3c4edf02-ea0b-457c-bd83-766c4021ada6"])
    links: LinksOutput
    lastName: str = OutputField(example_values=["Stripe"])
    firstName: str = OutputField(example_values=["xMeryl"])
    targetName: str = OutputField(example_values=["mstripe"])
    licenseType: str = OutputField(example_values=["FULL_USER"])
    recipientType: str = OutputField(example_values=["PERSON"])


class ProviderOutput(ActionOutput):
    id: str = OutputField(example_values=["(x)Matters Email Gateway"])


class MemberOutput(ActionOutput):
    id: str = OutputField(example_values=["828ef01a-1c11-4753-b13d-84816b4a270e"])
    site: SiteOutput
    links: LinksOutput
    status: str = OutputField(example_values=["ACTIVE"])
    language: str = OutputField(example_values=["en"])
    lastName: str = OutputField(example_values=["Bored"])
    timezone: str = OutputField(example_values=["US/Eastern"])
    webLogin: str = OutputField(example_values=["LR5dbyEu"])
    firstName: str = OutputField(example_values=["xHarrison"])
    targetName: str = OutputField(
        cef_types=["xmatters target name"], example_values=["hbored"]
    )
    licenseType: str = OutputField(example_values=["FULL_USER"])
    whenCreated: str = OutputField(example_values=["2021-07-01T06:19:56.439Z"])
    whenUpdated: str = OutputField(example_values=["2021-07-01T06:19:56.439Z"])
    recipientType: str = OutputField(example_values=["PERSON"])
    externallyOwned: bool = OutputField(example_values=[False])
    lastLogin: str = OutputField(example_values=["2021-12-31T05:19:42.930Z"])
    created: str = OutputField(example_values=["2021-07-01T06:19:56.439Z"])
    groupType: str = OutputField(example_values=["ON_CALL"])
    description: str = OutputField(
        example_values=[
            "Example group showing rotating daytime, evening and weekend shifts"
        ]
    )
    observedByAll: bool = OutputField(example_values=[True])
    allowDuplicates: bool = OutputField(example_values=[True])
    useDefaultDevices: bool = OutputField(example_values=[True])
    name: str = OutputField(example_values=["Work Email"])
    delay: float = OutputField(example_values=[1])
    owner: OwnerOutput
    provider: ProviderOutput
    sequence: float = OutputField(example_values=[1])
    deviceType: str = OutputField(example_values=["EMAIL"])
    privileged: bool = OutputField(example_values=[False])
    testStatus: str = OutputField(example_values=["UNTESTED"])
    emailAddress: str = OutputField(example_values=["test@test.com"])
    defaultDevice: bool = OutputField(example_values=[True])
    priorityThreshold: str = OutputField(example_values=["LOW"])


class DataOutput(ActionOutput):
    delay: float = OutputField(example_values=[1])
    member: MemberOutput
    position: float = OutputField(example_values=[1])
    escalationType: str = OutputField(example_values=["NONE"])


class MembersLinksOutput(ActionOutput):
    self: str = OutputField(
        example_values=[
            "/api/xm/1/groups/3c765cff-3fe3-4229-8dc4-6b41c3d701a2/shifts/97fbe2ff-430c-4700-af24-bf076c9aaf48/occurrences/2021-12-28T08:00:00.000Z/members?offset=0&limit=3"
        ]
    )
    next: str | None = OutputField(
        example_values=[
            "/api/xm/1/groups/ce423b4a-1ecd-48f9-a4ac-71cef75f9875/shifts/ed6fbddc-959c-4534-b932-e661a0ac01a3/occurrences/2021-12-28T22:00:00.000Z/members?offset=1&limit=1"
        ]
    )


class MembersOutput(ActionOutput):
    count: float = OutputField(example_values=[1])
    links: MembersLinksOutput
    total: float = OutputField(example_values=[1])
    data: list[DataOutput]


class GetOncallUserOutput(ActionOutput):
    group_name: str | None = OutputField(
        column_name="Group Name", example_values=["Service-Team-1"]
    )
    shift_name: str | None = OutputField(
        column_name="Shift Name", example_values=["Default Shift"]
    )
    shift_starts: str | None = OutputField(
        column_name="Shift Starts (GMT)",
        example_values=["2021-12-28T08:00:00Z"],
    )
    shift_ends: str | None = OutputField(
        column_name="Shift Ends (GMT)",
        example_values=["2021-12-29T08:00:00Z"],
    )
    oncall_info: str | None = OutputField(
        column_name="Oncall Info",
        example_values=["828ef01a... | hbored | PERSON | ACTIVE"],
    )
    end: str = OutputField(example_values=["2021-12-29T08:00:00Z"])
    group: GroupOutput
    shift: ShiftOutput
    start: str = OutputField(example_values=["2021-12-28T08:00:00Z"])
    members: MembersOutput


class GetOncallUserSummary(ActionOutput):
    next_page: str | None = OutputField(
        example_values=[
            "/api/xm/1/groups/ce423b4a-1ecd-48f9-a4ac-71cef75f9875/shifts/ed6fbddc-959c-4534-b932-e661a0ac01a3/occurrences/2021-12-28T22:00:00.000Z/members?offset=1&limit=1"
        ]
    )
    num_of_shifts: float | None = OutputField(example_values=[1])


@app.action(
    description="Get information about who is on call",
    action_type="investigate",
    read_only=True,
    render_as="table",
    summary_type=GetOncallUserSummary,
)
def get_oncall_user(
    params: GetOncallUserParams, asset: Asset, soar: SOARClient
) -> list[GetOncallUserOutput]:
    if bool(params.from_) != bool(params.to):
        raise ValueError("Please provide both from and to value for timeframe")
    if (
        params.members_per_shift is not None
        and not 1 <= params.members_per_shift <= 100
    ):
        raise ValueError(
            "Please provide a valid value from 1 to 100 for members_per_shift"
        )

    embeds = []
    if params.embed_shift:
        embeds.append("shift")
    if params.embed_owner:
        embeds.append("members.owner")
    query = {
        "embed": ",".join(embeds),
        "groups": ",".join(x.strip() for x in params.groups.split(",")),
    }
    if params.members_per_shift is not None:
        query["membersPerShift"] = int(params.members_per_shift)
    if params.from_ is not None:
        query["from"] = params.from_
    if params.to is not None:
        query["to"] = params.to

    payload = xmatters_request(asset, "GET", "/api/xm/1//on-call", params=query)
    rows = payload["data"]
    if not rows or "members" not in rows[0] or "count" not in rows[0]["members"]:
        raise ActionFailure("No shift found for the given input parameters")

    table_rows = []
    shift_count = 0
    for row in rows:
        table_row = dict(row)
        group = row.get("group") or {}
        shift = row.get("shift") or {}
        if shift:
            shift_count += 1
        members = (row.get("members") or {}).get("data") or []
        member_summaries = []
        for member_row in members:
            member = member_row.get("member") or {}
            values = [
                member.get("id"),
                member.get("targetName"),
                member.get("recipientType"),
                member.get("status"),
            ]
            values = [str(value) for value in values if value is not None]
            if values:
                member_summaries.append(" | ".join(values))

        table_row.update(
            {
                "group_name": group.get("targetName"),
                "shift_name": shift.get("name"),
                "shift_starts": row.get("start"),
                "shift_ends": row.get("end"),
                "oncall_info": "; ".join(member_summaries)
                if member_summaries
                else "This shift has no members",
            }
        )
        table_rows.append(table_row)

    members_links = (rows[0].get("members") or {}).get("links") or {}
    soar.set_summary(
        GetOncallUserSummary(
            next_page=members_links.get("next"), num_of_shifts=shift_count
        )
    )
    soar.set_message("Successfully retrieved who is on call")
    return build_output(GetOncallUserOutput, table_rows)
