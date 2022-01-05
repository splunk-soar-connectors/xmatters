[comment]: # "Auto-generated SOAR connector documentation"
# xMatters

Publisher: Splunk  
Connector Version: 2\.1\.2  
Product Vendor: xMatters  
Product Name: xMatters  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 5\.0\.0  

This app integrates with xMatters to retrieve information about events and users

[comment]: # " File: readme.md"
[comment]: # "  Copyright (c) 2017-2022 Splunk Inc."
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


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a xMatters asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**base\_url** |  required  | string | Base url, e\.g\. https\://my\-company\.xmatters\.com
**username** |  required  | string | Username
**password** |  required  | password | Password
**client\_id** |  optional  | string | Client ID\. OAuth will be preferred if provided

### Supported Actions  
[test connectivity](#action-test-connectivity) - Run a quick query on the server to check the connection and credentials  
[get event](#action-get-event) - Get information about a single event  
[update event](#action-update-event) - Update the status of an event  
[get user](#action-get-user) - Get information about a user  
[create event](#action-create-event) - Create \(trigger\) an event in xMatters  
[list users](#action-list-users) - Get information about multiple users matching a property name/value  
[list events](#action-list-events) - Query for specific events by providing a property name/value  
[list groups](#action-list-groups) - Get information about multiple groups matching a property  
[get oncall user](#action-get-oncall-user) - Get information about who is on call  

## action: 'test connectivity'
Run a quick query on the server to check the connection and credentials

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'get event'
Get information about a single event

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**event\_id** |  required  | Event ID | string |  `xmatters event id` 
**embed\_recipients** |  optional  | Embed Recipients | boolean | 
**embed\_response\_options** |  optional  | Embed Response Options | boolean | 
**targeted** |  optional  | Return directly targeted recipients | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.embed\_recipients | boolean | 
action\_result\.parameter\.embed\_response\_options | boolean | 
action\_result\.parameter\.event\_id | string |  `xmatters event id` 
action\_result\.parameter\.targeted | boolean | 
action\_result\.data\.\*\.bypassPhoneIntro | boolean | 
action\_result\.data\.\*\.created | string | 
action\_result\.data\.\*\.escalationOverride | boolean | 
action\_result\.data\.\*\.eventId | string |  `xmatters event id` 
action\_result\.data\.\*\.eventType | string | 
action\_result\.data\.\*\.expirationInMinutes | numeric | 
action\_result\.data\.\*\.floodControl | boolean | 
action\_result\.data\.\*\.form\.id | string |  `xmatters form uuid` 
action\_result\.data\.\*\.form\.name | string | 
action\_result\.data\.\*\.id | string |  `xmatters event id` 
action\_result\.data\.\*\.incident | string | 
action\_result\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.name | string | 
action\_result\.data\.\*\.notificationAuditCount | numeric | 
action\_result\.data\.\*\.overrideDeviceRestrictions | boolean | 
action\_result\.data\.\*\.plan\.id | string | 
action\_result\.data\.\*\.plan\.integrationConfigType | string | 
action\_result\.data\.\*\.plan\.name | string | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.recipients\.count | numeric | 
action\_result\.data\.\*\.recipients\.data\.\*\.externallyOwned | boolean | 
action\_result\.data\.\*\.recipients\.data\.\*\.firstName | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.id | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.language | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.lastName | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.recipientType | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.site\.id | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.site\.links\.self | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.site\.name | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.status | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.recipients\.data\.\*\.targeted | boolean | 
action\_result\.data\.\*\.recipients\.data\.\*\.timezone | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.webLogin | string | 
action\_result\.data\.\*\.recipients\.links\.self | string | 
action\_result\.data\.\*\.recipients\.total | numeric | 
action\_result\.data\.\*\.requirePhonePassword | boolean | 
action\_result\.data\.\*\.responseCountsEnabled | boolean | 
action\_result\.data\.\*\.responseOptions\.count | numeric | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.action | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.allowComments | boolean | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.contribution | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.description | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.id | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.joinConference | boolean | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.number | numeric | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.order | numeric | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.prompt | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.redirectUrl | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.text | string | 
action\_result\.data\.\*\.responseOptions\.total | numeric | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.submitter\.firstName | string | 
action\_result\.data\.\*\.submitter\.id | string |  `xmatters user id` 
action\_result\.data\.\*\.submitter\.lastName | string | 
action\_result\.data\.\*\.submitter\.links\.self | string | 
action\_result\.data\.\*\.submitter\.recipientType | string | 
action\_result\.data\.\*\.submitter\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.terminated | string | 
action\_result\.data\.\*\.voicemailOptions\.every | numeric | 
action\_result\.data\.\*\.voicemailOptions\.leave | string | 
action\_result\.data\.\*\.voicemailOptions\.retry | numeric | 
action\_result\.summary\.event\_id | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'update event'
Update the status of an event

Type: **generic**  
Read only: **False**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**event\_id** |  required  | Event ID | string |  `xmatters event id` 
**status** |  required  | Status of the event | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.event\_id | string |  `xmatters event id` 
action\_result\.parameter\.status | string | 
action\_result\.data\.\*\.bypassPhoneIntro | boolean | 
action\_result\.data\.\*\.created | string | 
action\_result\.data\.\*\.escalationOverride | boolean | 
action\_result\.data\.\*\.eventId | string |  `xmatters event id` 
action\_result\.data\.\*\.eventType | string | 
action\_result\.data\.\*\.expirationInMinutes | numeric | 
action\_result\.data\.\*\.floodControl | boolean | 
action\_result\.data\.\*\.form\.id | string | 
action\_result\.data\.\*\.id | string | 
action\_result\.data\.\*\.incident | string | 
action\_result\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.notificationAuditCount | numeric | 
action\_result\.data\.\*\.overrideDeviceRestrictions | boolean | 
action\_result\.data\.\*\.priority | string | 
action\_result\.data\.\*\.recipients\.count | numeric | 
action\_result\.data\.\*\.recipients\.data\.\*\.externallyOwned | boolean | 
action\_result\.data\.\*\.recipients\.data\.\*\.firstName | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.id | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.language | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.lastName | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.recipientType | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.site\.id | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.site\.links\.self | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.site\.name | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.status | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.recipients\.data\.\*\.targeted | boolean | 
action\_result\.data\.\*\.recipients\.data\.\*\.timezone | string | 
action\_result\.data\.\*\.recipients\.data\.\*\.webLogin | string | 
action\_result\.data\.\*\.recipients\.links\.self | string | 
action\_result\.data\.\*\.recipients\.total | numeric | 
action\_result\.data\.\*\.requirePhonePassword | boolean | 
action\_result\.data\.\*\.responseOptions\.count | numeric | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.action | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.contribution | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.description | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.joinConference | boolean | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.number | numeric | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.prompt | string | 
action\_result\.data\.\*\.responseOptions\.data\.\*\.text | string | 
action\_result\.data\.\*\.responseOptions\.total | numeric | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.submitter\.firstName | string | 
action\_result\.data\.\*\.submitter\.id | string |  `xmatters user id` 
action\_result\.data\.\*\.submitter\.lastName | string | 
action\_result\.data\.\*\.submitter\.links\.self | string | 
action\_result\.data\.\*\.submitter\.recipientType | string | 
action\_result\.data\.\*\.submitter\.targetName | string |  `xmatters target name` 
action\_result\.summary\.event\_id | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'get user'
Get information about a user

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**identifier** |  required  | Either the Target Name or ID of the user | string |  `xmatters target name`  `xmatters user id` 
**embed\_roles** |  optional  | Include a list of each user's role | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.embed\_roles | boolean | 
action\_result\.parameter\.identifier | string |  `xmatters target name`  `xmatters user id` 
action\_result\.data\.\*\.externallyOwned | boolean | 
action\_result\.data\.\*\.firstName | string | 
action\_result\.data\.\*\.id | string |  `xmatters user id` 
action\_result\.data\.\*\.language | string | 
action\_result\.data\.\*\.lastLogin | string | 
action\_result\.data\.\*\.lastName | string | 
action\_result\.data\.\*\.licenseType | string | 
action\_result\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.recipientType | string | 
action\_result\.data\.\*\.roles\.count | numeric | 
action\_result\.data\.\*\.roles\.data\.\*\.description | string | 
action\_result\.data\.\*\.roles\.data\.\*\.id | string | 
action\_result\.data\.\*\.roles\.data\.\*\.name | string | 
action\_result\.data\.\*\.roles\.total | numeric | 
action\_result\.data\.\*\.site\.id | string | 
action\_result\.data\.\*\.site\.links\.self | string | 
action\_result\.data\.\*\.site\.name | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.timezone | string | 
action\_result\.data\.\*\.webLogin | string | 
action\_result\.data\.\*\.whenCreated | string | 
action\_result\.data\.\*\.whenUpdated | string | 
action\_result\.summary\.person\_id | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'create event'
Create \(trigger\) an event in xMatters

Type: **generic**  
Read only: **False**

See <a href="https\://help\.xmatters\.com/OnDemand/xmodwelcome/communicationplanbuilder/appendixrestapi\.htm?cshid=apiPOSTtrigger\#POSTtrigger">this link</a> for more information on the parameters\. The input expects the actual string literal representations of their respective fields\. Lists need to be enclosed in square braces, objects in curly braces, etc\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**form\_uuid** |  required  | The Form UUID | string |  `xmatters form uuid` 
**recipients** |  required  | Comma\-separated list of user names | string | 
**properties** |  optional  | A JSON object of property names and values | string | 
**callbacks** |  optional  | The list of Event Update Callback Objects | string | 
**priority** |  optional  | The priority of the event | string | 
**conferences** |  optional  | The list of conferences bridges | string | 
**responses** |  optional  | The comma\-separated list of response option UUIDs | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.callbacks | string | 
action\_result\.parameter\.conferences | string | 
action\_result\.parameter\.form\_uuid | string |  `xmatters form uuid` 
action\_result\.parameter\.priority | string | 
action\_result\.parameter\.properties | string | 
action\_result\.parameter\.recipients | string | 
action\_result\.parameter\.responses | string | 
action\_result\.data\.\*\.id | string |  `xmatters event id` 
action\_result\.summary\.event\_id | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list users'
Get information about multiple users matching a property name/value

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**search** |  optional  | Search term\. Will check first name, last name, web login, etc\. Separate values with either space or a \+ sign | string | 
**embed\_roles** |  optional  | Include a list of each users' roles | boolean | 
**property\_name** |  optional  | Comma\-separated list of property names | string | 
**property\_value** |  optional  | Comma\-separated list of property values | string | 
**offset** |  optional  | Number of items to skip before returning results | numeric | 
**limit** |  optional  | The number of items to return | numeric | 
**page\_uri** |  optional  | URI For the page | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.embed\_roles | boolean | 
action\_result\.parameter\.limit | numeric | 
action\_result\.parameter\.offset | numeric | 
action\_result\.parameter\.page\_uri | string | 
action\_result\.parameter\.property\_name | string | 
action\_result\.parameter\.property\_value | string | 
action\_result\.parameter\.search | string | 
action\_result\.data\.\*\.count | numeric | 
action\_result\.data\.\*\.data\.\*\.externallyOwned | boolean | 
action\_result\.data\.\*\.data\.\*\.firstName | string | 
action\_result\.data\.\*\.data\.\*\.id | string | 
action\_result\.data\.\*\.data\.\*\.language | string | 
action\_result\.data\.\*\.data\.\*\.lastLogin | string | 
action\_result\.data\.\*\.data\.\*\.lastName | string | 
action\_result\.data\.\*\.data\.\*\.licenseType | string | 
action\_result\.data\.\*\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.data\.\*\.recipientType | string | 
action\_result\.data\.\*\.data\.\*\.roles\.count | numeric | 
action\_result\.data\.\*\.data\.\*\.roles\.data\.\*\.description | string | 
action\_result\.data\.\*\.data\.\*\.roles\.data\.\*\.id | string | 
action\_result\.data\.\*\.data\.\*\.roles\.data\.\*\.name | string | 
action\_result\.data\.\*\.data\.\*\.roles\.total | numeric | 
action\_result\.data\.\*\.data\.\*\.site\.id | string | 
action\_result\.data\.\*\.data\.\*\.site\.links\.self | string | 
action\_result\.data\.\*\.data\.\*\.site\.name | string | 
action\_result\.data\.\*\.data\.\*\.status | string | 
action\_result\.data\.\*\.data\.\*\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.data\.\*\.timezone | string | 
action\_result\.data\.\*\.data\.\*\.webLogin | string | 
action\_result\.data\.\*\.data\.\*\.whenCreated | string | 
action\_result\.data\.\*\.data\.\*\.whenUpdated | string | 
action\_result\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.total | numeric | 
action\_result\.summary\.people\_returned | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list events'
Query for specific events by providing a property name/value

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**property\_name** |  optional  | Comma\-separated list of property names | string | 
**property\_value** |  optional  | Comma\-separated list of property values | string | 
**offset** |  optional  | Number of items to skip before returning results | numeric | 
**limit** |  optional  | The number of items to return | numeric | 
**status** |  optional  | Status of the event | string | 
**from** |  optional  | A date in UTC Format for the start of a time range to search | string | 
**to** |  optional  | A date in UTC Format for the end of a time range to search | string | 
**page\_uri** |  optional  | URI For the page | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.parameter\.from | string | 
action\_result\.parameter\.limit | numeric | 
action\_result\.parameter\.offset | numeric | 
action\_result\.parameter\.page\_uri | string | 
action\_result\.parameter\.property\_name | string | 
action\_result\.parameter\.property\_value | string | 
action\_result\.parameter\.status | string | 
action\_result\.parameter\.to | string | 
action\_result\.data\.\*\.count | numeric | 
action\_result\.data\.\*\.data\.\*\.bypassPhoneIntro | boolean | 
action\_result\.data\.\*\.data\.\*\.created | string | 
action\_result\.data\.\*\.data\.\*\.escalationOverride | boolean | 
action\_result\.data\.\*\.data\.\*\.eventId | string |  `xmatters event id` 
action\_result\.data\.\*\.data\.\*\.eventType | string | 
action\_result\.data\.\*\.data\.\*\.floodControl | boolean | 
action\_result\.data\.\*\.data\.\*\.form\.id | string | 
action\_result\.data\.\*\.data\.\*\.form\.name | string | 
action\_result\.data\.\*\.data\.\*\.id | string |  `xmatters event id` 
action\_result\.data\.\*\.data\.\*\.incident | string | 
action\_result\.data\.\*\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.data\.\*\.name | string | 
action\_result\.data\.\*\.data\.\*\.overrideDeviceRestrictions | boolean | 
action\_result\.data\.\*\.data\.\*\.plan\.id | string | 
action\_result\.data\.\*\.data\.\*\.plan\.integrationConfigType | string | 
action\_result\.data\.\*\.data\.\*\.plan\.name | string | 
action\_result\.data\.\*\.data\.\*\.priority | string | 
action\_result\.data\.\*\.data\.\*\.relatedIncident\.id | string | 
action\_result\.data\.\*\.data\.\*\.relatedIncident\.links\.self | string | 
action\_result\.data\.\*\.data\.\*\.requestId | string | 
action\_result\.data\.\*\.data\.\*\.requirePhonePassword | boolean | 
action\_result\.data\.\*\.data\.\*\.responseCountsEnabled | boolean | 
action\_result\.data\.\*\.data\.\*\.status | string | 
action\_result\.data\.\*\.data\.\*\.submitter\.firstName | string | 
action\_result\.data\.\*\.data\.\*\.submitter\.id | string |  `xmatters user id` 
action\_result\.data\.\*\.data\.\*\.submitter\.lastName | string | 
action\_result\.data\.\*\.data\.\*\.submitter\.links\.self | string | 
action\_result\.data\.\*\.data\.\*\.submitter\.recipientType | string | 
action\_result\.data\.\*\.data\.\*\.submitter\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.data\.\*\.terminated | string | 
action\_result\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.total | numeric | 
action\_result\.summary\.events\_returned | string | 
action\_result\.summary\.next\_page | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'list groups'
Get information about multiple groups matching a property

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**search\_group** |  optional  | Search term will check in name and description of groups\. Separate multiple values with either space or a \+ sign | string | 
**members** |  optional  | The targetName or id of users, dynamic teams or devices that are part of a group\. Separate multiple values with commma | string | 
**status** |  optional  | Status of the group | string | 
**embed\_observers** |  optional  | Includes a list of observers for a group | boolean | 
**embed\_supervisors** |  optional  | Includes a list of supervisors for a group | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.parameter\.search\_group | string | 
action\_result\.parameter\.members | string | 
action\_result\.parameter\.status | string | 
action\_result\.parameter\.embed\_observers | boolean | 
action\_result\.parameter\.embed\_supervisors | boolean | 
action\_result\.summary\.groups\_returned | numeric | 
action\_result\.data\.\*\.id | string |  `xmatters group id` 
action\_result\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.status | string | 
action\_result\.data\.\*\.created | string | 
action\_result\.data\.\*\.groupType | string | 
action\_result\.data\.\*\.targetName | string |  `xmatters group name` 
action\_result\.data\.\*\.description | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.id | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.site\.id | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.site\.name | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.site\.links\.self | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.links\.self | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.status | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.language | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.lastName | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.timezone | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.webLogin | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.firstName | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.lastLogin | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.targetName | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.licenseType | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.whenCreated | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.whenUpdated | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.recipientType | string | 
action\_result\.data\.\*\.supervisors\.data\.\*\.externallyOwned | boolean | 
action\_result\.data\.\*\.supervisors\.count | numeric | 
action\_result\.data\.\*\.supervisors\.links\.self | string | 
action\_result\.data\.\*\.supervisors\.total | numeric | 
action\_result\.data\.\*\.observedByAll | boolean | 
action\_result\.data\.\*\.recipientType | string | 
action\_result\.data\.\*\.allowDuplicates | boolean | 
action\_result\.data\.\*\.externallyOwned | boolean | 
action\_result\.data\.\*\.useDefaultDevices | boolean | 
action\_result\.data\.\*\.observers\.data\.\*\.id | string | 
action\_result\.data\.\*\.observers\.data\.\*\.name | string | 
action\_result\.data\.\*\.observers\.data\.\*\.description | string | 
action\_result\.data\.\*\.observers\.count | numeric | 
action\_result\.data\.\*\.observers\.total | numeric |   

## action: 'get oncall user'
Get information about who is on call

Type: **investigate**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**groups** |  required  | Name or id of a group\. Separate multiple values with commma | string |  `xmatters group id`  `xmatters group name` 
**members\_per\_shift** |  optional  | The number of shift members to include \(Default\: 3, Max\: 100\) | numeric | 
**from** |  optional  | Date time value in UTC format \(Eg\. 2022\-01\-01T03\:00\:00Z\) | string | 
**to** |  optional  | Date time value in UTC format \(Eg\. 2022\-01\-01T04\:00\:00Z\) | string | 
**embed\_shift** |  optional  | Includes shift details | boolean | 
**embed\_owner** |  optional  | Includes members owner details | boolean | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.status | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric | 
action\_result\.parameter\.groups | string |  `xmatters group id`  `xmatters group name` 
action\_result\.parameter\.members\_per\_shift | numeric | 
action\_result\.parameter\.from | string | 
action\_result\.parameter\.to | string | 
action\_result\.parameter\.embed\_shift | boolean | 
action\_result\.parameter\.embed\_owner | boolean | 
action\_result\.summary\.num\_of\_shifts | numeric | 
action\_result\.data\.\*\.end | string | 
action\_result\.data\.\*\.group\.id | string | 
action\_result\.data\.\*\.group\.links\.self | string | 
action\_result\.data\.\*\.group\.groupType | string | 
action\_result\.data\.\*\.group\.targetName | string | 
action\_result\.data\.\*\.group\.recipientType | string | 
action\_result\.data\.\*\.shift\.id | string | 
action\_result\.data\.\*\.shift\.name | string | 
action\_result\.data\.\*\.shift\.links\.self | string | 
action\_result\.data\.\*\.start | string | 
action\_result\.data\.\*\.members\.count | numeric | 
action\_result\.data\.\*\.members\.links\.self | string | 
action\_result\.data\.\*\.members\.total | numeric | 
action\_result\.data\.\*\.members\.data\.\*\.delay | numeric | 
action\_result\.data\.\*\.members\.data\.\*\.member\.id | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.site\.id | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.site\.name | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.site\.links\.self | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.links\.self | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.status | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.language | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.lastName | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.timezone | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.webLogin | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.firstName | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.targetName | string |  `xmatters target name` 
action\_result\.data\.\*\.members\.data\.\*\.member\.licenseType | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.whenCreated | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.whenUpdated | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.recipientType | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.externallyOwned | boolean | 
action\_result\.data\.\*\.members\.data\.\*\.position | numeric | 
action\_result\.data\.\*\.members\.data\.\*\.escalationType | string | 
action\_result\.data\.\*\.shift\.end | string | 
action\_result\.data\.\*\.shift\.group\.id | string | 
action\_result\.data\.\*\.shift\.group\.links\.self | string | 
action\_result\.data\.\*\.shift\.group\.groupType | string | 
action\_result\.data\.\*\.shift\.group\.targetName | string | 
action\_result\.data\.\*\.shift\.group\.recipientType | string | 
action\_result\.data\.\*\.shift\.start | string | 
action\_result\.data\.\*\.shift\.timezone | string | 
action\_result\.data\.\*\.shift\.recurrence\.end\.endBy | string | 
action\_result\.data\.\*\.shift\.recurrence\.frequency | string | 
action\_result\.data\.\*\.shift\.recurrence\.repeatEvery | numeric | 
action\_result\.data\.\*\.members\.links\.next | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.lastLogin | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.created | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.groupType | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.description | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.observedByAll | boolean | 
action\_result\.data\.\*\.members\.data\.\*\.member\.allowDuplicates | boolean | 
action\_result\.data\.\*\.members\.data\.\*\.member\.useDefaultDevices | boolean | 
action\_result\.data\.\*\.members\.data\.\*\.member\.name | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.delay | numeric | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.id | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.links\.self | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.lastName | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.firstName | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.targetName | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.licenseType | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.owner\.recipientType | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.provider\.id | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.sequence | numeric | 
action\_result\.data\.\*\.members\.data\.\*\.member\.deviceType | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.privileged | boolean | 
action\_result\.data\.\*\.members\.data\.\*\.member\.testStatus | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.emailAddress | string | 
action\_result\.data\.\*\.members\.data\.\*\.member\.defaultDevice | boolean | 
action\_result\.data\.\*\.members\.data\.\*\.member\.priorityThreshold | string | 