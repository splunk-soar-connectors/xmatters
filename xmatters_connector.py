# --
# File: xmatters_connector.py
#
# Copyright (c) Phantom Cyber Corporation, 2014-2017
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

# Phantom Imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Const Imports
from xmatters_consts import *

# Generic Imports
import requests
import urllib
import re
import simplejson as json
from bs4 import BeautifulSoup


APP_PARAM_TO_API_PARAM_MAP = {
    "property_name": "propertyName",
    "property_value": "propertyValue",
}

DECODE_JSON_PARAMETERS = [
    'recipients', 'properties',
    'callbacks', 'conferences',
    'response'
]


class RetVal(tuple):
    def __new__(cls, val1, val2):
        return tuple.__new__(RetVal, (val1, val2))


class XMattersConnector(BaseConnector):
    ACTION_ID_LIST_EVENTS = "list_events"
    ACTION_ID_GET_EVENT = "get_event"
    ACTION_ID_UPDATE_EVENT = "update_event"
    ACTION_ID_LIST_PEOPLE = "list_people"
    ACTION_ID_GET_PERSON = "get_person"
    ACTION_ID_INITIATE_EVENT = "initiate_event"

    def __init__(self):
        super(XMattersConnector, self).__init__()
        self._base_url = None
        self._username = None
        self._password = None
        self._client_id = None
        self._use_token = False
        self._state = {}
        self._oauth_obj = None
        return

    def initialize(self):
        config = self.get_config()
        self._base_url = config[XM_CONFIG_BASE_URL]
        self._client_id = config.get(XM_CONFIG_CLIENT_ID, None)
        if (self._client_id):
            self._use_token = True

        self._state = self.load_state()
        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)
        return phantom.APP_SUCCESS

    def _process_empty_reponse(self, response, action_result):

        if (200 <= response.status_code < 205):
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(action_result.set_status(phantom.APP_ERROR, "Empty response and no information in the header"), None)

    def _process_html_response(self, response, action_result):

        # An html response, is bound to be an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = "Status Code: {0}. Data from server:\n{1}\n".format(status_code,
                error_text)

        message = message.replace('{', '{{').replace('}', '}}')

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):

        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            self.save_progress('Cannot parse JSON')
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to parse response as JSON", e), None)

        if (200 <= r.status_code < 205):
            return RetVal(phantom.APP_SUCCESS, resp_json)

        action_result.add_data(resp_json)
        message = r.text.replace('{', '{{').replace('}', '}}')
        return RetVal( action_result.set_status( phantom.APP_ERROR, "Error from server, Status Code: {0} data returned: {1}".format(r.status_code, message)), resp_json)

    def _process_response(self, r, action_result):

        # store the r_text in debug data, it will get dumped in the logs if an error occurs
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # There are just too many differences in the response to handle all of them in the same function
        if ('json' in r.headers.get('Content-Type', '')):
            return self._process_json_response(r, action_result)

        if ('html' in r.headers.get('Content-Type', '')):
            return self._process_html_response(r, action_result)

        # it's not an html or json, handle if it is a successfull empty reponse
        if (200 <= r.status_code < 205) and (not r.text):
            return self._process_empty_reponse(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _make_rest_call(self, action_result, endpoint, params={}, body={}, headers={}, method="get", auth=None):
        """ Returns 2 values, use RetVal """

        url = self._base_url + endpoint

        try:
            request_func = getattr(requests, method)
        except AttributeError:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unsupported method: {0}".format(method)), None)
        except Exception as e:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Handled exception: {0}".format(str(e))), None)

        try:
            response = request_func(url, params=params, json=body, headers=headers, auth=auth)
        except Exception as e:
            # Set the action_result status to error, the handler function will most probably return as is
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Error connecting: {0}".format(str(e))), None)

        self.debug_print(response.url)

        return self._process_response(response, action_result)

    def _create_headers(self, h={}, **kwargs):
        d = {}
        d['Content-Type'] = 'application/json'
        d.update(h)
        for k, v in kwargs.iteritems():
            d[k] = v
        return d

    def _get_new_oauth_token(self, action_result):
        """Generate a new oauth token using the refresh token, if available
        """
        params = {}
        params['client_id'] = self._client_id
        try:
            params['refresh_token'] = self._state['oauth_token']['refresh_token']
            params['grant_type'] = "refresh_token"
        except KeyError:
            config = self.get_config()
            params['username'] = config[XM_CONFIG_USERNAME]
            params['password'] = config[XM_CONFIG_PASSWORD]
            params['grant_type'] = "password"

        headers = self._create_headers()
        ret_val, response_json = self._make_rest_call(action_result, '/api/xm/1/oauth2/token', params=params, headers=headers, method="post")

        if (phantom.is_fail(ret_val)):
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Error in token request"), None)

        self._state['oauth_token'] = response_json
        try:
            return RetVal(phantom.APP_SUCCESS, response_json['access_token'])
        except Exception as e:
            self._state = {}
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to parse access token", e), None)

    def _get_oauth_token(self, action_result):
        return self._get_new_oauth_token(action_result)

    def _get_authorization_credentials(self, action_result):
        auth = None
        headers = {}
        auth = None
        if (self._use_token):
            self.save_progress("Connecting with OAuth Token")
            ret_val, oauth_token = self._get_oauth_token(action_result)
            if (phantom.is_fail(ret_val)):
                return ret_val, None, None
            self.save_progress("OAuth Token Retrieved")
            headers = self._create_headers({'Authorization': 'Bearer {0}'.format(oauth_token)})
        else:
            ret_val = phantom.APP_SUCCESS
            self.save_progress("Connecting without OAuth Token")
            config = self.get_config()
            auth = requests.auth.HTTPBasicAuth(config[XM_CONFIG_USERNAME], config[XM_CONFIG_PASSWORD])
            headers = self._create_headers()

        return ret_val, auth, headers

    def _format_params_to_query(self, params):
        """If you just pass with the params argument into the request, commas will be encoded to %2C
           The API uses literal commas and %2C differently. %2C would is for when the actual field has a comma, and
           ',' is for creating a list in the query.
           For example: ?propertyName=isTure,floor&propertyValue=false,Balcony%2Cupper
           %1A is the code for substitute character, which seemed fitting and unused
        """
        for k, v in params.iteritems():
            if "%1A" in v:
                self.debug_print("I'm so sorry")
            self.debug_print(v)
            v.replace("%2C", "%1A")

        return urllib.urlencode(params).replace("%2C", ",").replace("%252C", "%2C")

    def _test_connectivity(self, param):
        action_result = ActionResult()
        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return self.set_status_save_progress(phantom.APP_ERROR, "Connectivity test failed")

        self.save_progress('Making Request')
        ret_val, response_json = self._make_rest_call(action_result, '/api/xm/1/ping', headers=headers, auth=auth)

        if (phantom.is_fail(ret_val)):
            return self.set_status_save_progress(phantom.APP_ERROR, "Connectivity test failed")
        else:
            return self.set_status_save_progress(phantom.APP_SUCCESS, "Connectivity test succeeded")

    def _list_events(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        params = {}

        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return ret_val

        # Prefer the next page if provided
        try:
            endpoint = param['page_uri']
        except KeyError:
            regex = re.compile(r",\s+")
            for k, v in param.iteritems():
                if k == 'context':
                    continue
                params[APP_PARAM_TO_API_PARAM_MAP.get(k, k)] = regex.sub(",", str(v))
            endpoint = '/api/xm/1/events'
            endpoint += '?' + self._format_params_to_query(params)

        ret_val, response_json = self._make_rest_call(action_result, endpoint, headers=headers, auth=auth)

        if (phantom.is_fail(ret_val)):
            return ret_val

        action_result.add_data(response_json)
        try:
            action_result.set_summary({'next_page': response_json['links']['next']})
        except KeyError:
            pass
        return action_result.set_status(phantom.APP_SUCCESS)

    def _initiate_event(self, param):
        """This API is going to be depreciated 'soon'. If this action suddenly and/or violently
           stops functioning, that is probably what happened
        """
        action_result = self.add_action_result(ActionResult(dict(param)))  # noqa

        endpoint = "reapi/2015-04-01/forms/{0}/triggers"  # noqa

        body = {}  # noqa

        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return ret_val

        for k, v in param.iteritems():
            if k == 'context':
                continue
            elif k in (DECODE_JSON_PARAMETERS):
                try:
                    body[k] = json.loads(v)
                except Exception as e:
                    self.debug_print(k)
                    self.debug_print(v)
                    self.debug_print(json.__version__)
                    return action_result.set_status(phantom.APP_ERROR, "Unable to parse string to json: {0}".format(str(e)))
            else:
                body[k] = v

        self.debug_print(body)

        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_event(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        params = {}

        event_id = param['event_id']
        endpoint = '/api/xm/1/events/{0}'.format(event_id)

        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return ret_val

        embed = []
        if param.get('embed_recipients', False):
            embed.append("recipients")
            params['targeted'] = param.get('targeted', False)

        if param.get('embed_response_object', False):
            embed.append("responseObject")

        if embed:
            params['embed'] = ",".join(embed)

        endpoint += '?' + self._format_params_to_query(params)
        ret_val, response_json = self._make_rest_call(action_result, endpoint, headers=headers, auth=auth)

        if (phantom.is_fail(ret_val)):
            return ret_val

        action_result.add_data(response_json)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _update_event(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        body = {}

        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return ret_val

        endpoint = '/api/xm/1/events'

        body['id'] = param['event_id']
        body['status'] = param['status']

        ret_val, response_json = self._make_rest_call(action_result, endpoint, headers=headers, body=body, auth=auth, method="post")

        if (phantom.is_fail(ret_val)):
            return ret_val

        action_result.add_data(response_json)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _list_people(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        params = {}

        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return ret_val

        try:
            endpoint = param['page_uri']
        except KeyError:
            regex = re.compile(r",\s+")
            for k, v in param.iteritems():
                if k == 'context':
                    continue
                if k == 'embed_roles':
                    params['embed'] = 'roles'
                params[APP_PARAM_TO_API_PARAM_MAP.get(k, k)] = regex.sub(",", str(v))
            endpoint = '/api/xm/1/people'
            endpoint += '?' + self._format_params_to_query(params)

        ret_val, response_json = self._make_rest_call(action_result, endpoint, headers=headers, auth=auth)

        if (phantom.is_fail(ret_val)):
            return ret_val

        action_result.add_data(response_json)
        try:
            action_result.set_summary({'next_page': response_json['links']['next']})
        except KeyError:
            pass
        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_person(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        params = {}

        person_id = param['identifier']
        endpoint = '/api/xm/1/people/{0}'.format(person_id)

        ret_val, auth, headers = self._get_authorization_credentials(action_result)
        if (phantom.is_fail(ret_val)):
            return ret_val

        if param.get('embed_roles', False):
            params['embed'] = 'roles'

        ret_val, response_json = self._make_rest_call(action_result, endpoint, params=params, headers=headers, auth=auth)

        if (phantom.is_fail(ret_val)):
            return ret_val

        action_result.add_data(response_json)
        return action_result.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param):
        result = None
        action = self.get_action_identifier()

        if (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            result = self._test_connectivity(param)
        if (action == self.ACTION_ID_LIST_EVENTS):
            result = self._list_events(param)
        if (action == self.ACTION_ID_GET_EVENT):
            result = self._get_event(param)
        if (action == self.ACTION_ID_UPDATE_EVENT):
            result = self._update_event(param)
        if (action == self.ACTION_ID_LIST_PEOPLE):
            result = self._list_people(param)
        if (action == self.ACTION_ID_GET_PERSON):
            result = self._get_person(param)
        if (action == self.ACTION_ID_INITIATE_EVENT):
            result = self._initiate_event(param)

        return result


if __name__ == '__main__':

    import sys
    import pudb
    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = XMattersConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print json.dumps(json.loads(ret_val), indent=4)

    exit(0)
