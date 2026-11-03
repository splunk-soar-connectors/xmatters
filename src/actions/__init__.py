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
"""Action modules registered with the xMatters SOAR app."""

from . import connectivity as test_connectivity
from . import get_event
from . import update_event
from . import get_person
from . import initiate_event
from . import list_people
from . import list_events
from . import list_groups
from . import get_oncall_user
from . import make_request

__all__ = [
    "get_event",
    "get_oncall_user",
    "get_person",
    "initiate_event",
    "list_events",
    "list_groups",
    "list_people",
    "make_request",
    "test_connectivity",
    "update_event",
]
