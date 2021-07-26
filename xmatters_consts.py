# File: xmatters_consts.py
# Copyright (c) 2017-2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.
PHANTOM_ERR_CODE_UNAVAILABLE = "Error code unavailable"
PHANTOM_ERR_MSG_UNAVAILABLE = "Unknown error occurred. Please check the asset configuration and|or action parameters."

XM_EXCEPTION_CAUGHT = "Exception caught: {0}"

XM_CONFIG_USERNAME = "username"
XM_CONFIG_PASSWORD = "password"
XM_CONFIG_BASE_URL = "base_url"
XM_CONFIG_CLIENT_ID = "client_id"

XM_ENDPOINT_TEST_CONNECTIVITY = '/api/xm/1/events?limit=1'
XM_ENDPOINT_LIST_EVENTS = '/api/xm/1/events'
XM_ENDPOINT_TRIGGER_EVENT = "/reapi/2015-04-01/forms/{0}/triggers"
XM_ENDPOINT_GET_EVENT = '/api/xm/1/events/{0}'
XM_ENDPOINT_UPDATE_EVENT = '/api/xm/1/events'
XM_ENDPOINT_LIST_PEOPLE = '/api/xm/1/people'
XM_ENDPOINT_GET_PEOPLE = '/api/xm/1/people/{0}'

XM_SUCC_TEST_CONNECTIVITY = "Test Connectivity Passed"
XM_LIST_EVENTS_SUCCESS = "Events retrieved successfully"
XM_CREATE_EVENT_SUCCESS = "Event created successfully"
XM_GET_EVENT_SUCCESS = "Successfully retrieved event"
XM_UPDATE_EVENT_SUCCESS = "Successfully updated event"
XM_LIST_PEOPLE_SUCCESS = "Users retrieved successfully"
XM_GET_PERSON_SUCCESS = "Successfully retrieved user"

XM_ERR_TOKEN_REQUEST = "Error in token request"
XM_ERR_PARSE_ACCESS_TOKEN = "Unable to parse access token"
XM_ERR_AUTHORIZE_OAUTH_TOKEN = "Unable to authorize with OAuth token"
XM_ERR_INVALID_JSON_PARAMS = "Unable to parse parameter '{0}' to json: {1}"

XM_ERR_TEST_CONNECTIVITY_FAILED = "Test Connectivity Failed"
