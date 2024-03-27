[comment]: # " File: README.md"
[comment]: # "  Copyright (c) 2017-2024 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
## Historical Data Access

You can access historical data using to and from. By setting the to and from parameters to dates in
the past, you automatically query historical data to return results. However, you cannot have a
timeframe that spans from the past to the future and there is a 24-hour synchronization window for
on-call data before it is available. This is to ensure that if you request on-call data for the
current day, the request doesn’t try to simultaneously draw data from both historical data and the
runtime data. For historical data queries, the length of time you can set is limited by your pricing
plan. Please refer [Accessing Data](https://help.xmatters.com/xmapi/#accessing-data) for more
details.

## Port Information

The app uses HTTP/ HTTPS protocol for communicating with the xMatters server. Below are the default
ports used by Splunk SOAR.

|         Service Name | Transport Protocol | Port |
|----------------------|--------------------|------|
|         http         | tcp                | 80   |
|         https        | tcp                | 443  |
