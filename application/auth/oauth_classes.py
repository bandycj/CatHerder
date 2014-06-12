import urllib
import urlparse

from flask import url_for, redirect
import requests
from application import application
from config.config_enums import ConfigKey


__author__ = 'Chris'


class OAuthService:
    def __init__(self, oauth_service):
        self.name = oauth_service.value
        if oauth_service in application.config['OAUTH_CONFIG']:
            config = application.config['OAUTH_CONFIG'][oauth_service]
            self.service_login_url = config[ConfigKey.SERVICE_LOGIN_URL]
            self.access_token_url = config[ConfigKey.ACCESS_TOKEN_URL]
            self.user_info_url = config[ConfigKey.USER_INFO_URL]
            self.client_id = config[ConfigKey.CLIENT_ID]
            self.client_secret = config[ConfigKey.CLIENT_SECRET]
        else:
            raise OAuthConfigException('No configuration for %s found' % (oauth_service.value))

    def access_token_requester(self, f):
        """
        Sets the helper method to handle how the provider actually accpets access_token requests.
        (i.e. facebook wants a GET and google wants a POST).
        :param f: a function which will send the request appropriately.
        :return: a dict of results which should contain an access_token.
        """
        self.request_access_token = f

    def user_info_requester(self, f):
        """
        Sets the helper method to account for providers returning common data with different key names.
        (i.e. user_name and userName).
        :param f: a function which access the input json dict by the correct keys.
        :return: the normalized data.
        """
        self.request_user_info = f

    def redirect_service_login(self):
        params = {
            'scope': 'email',
            'redirect_uri': url_for('authorized', service=self.name, _external=True),
            'response_type': 'code',
            'client_id': self.client_id
        }
        return redirect(self.service_login_url + '?' + urllib.urlencode(params))

    def get_access_token(self, request_url):
        """
        Exchange the authorization code for an access token.

        :param request_url: the url returned from step 1.
        :return: the access token or an error.
        """
        parsed = urlparse.urlparse(request_url)
        response = urlparse.parse_qs(parsed.query)
        if 'code' in response:
            auth_code = response['code'][0]
            params = {
                'code': auth_code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': url_for('authorized', service=self.name, _external=True),
                'grant_type': 'authorization_code'
            }
            try:
                return self.request_access_token(self.access_token_url, params)
            except ValueError as e:
                return {'error': e.message}
        return {'error': 'unknown'}

    def get_user_info(self, auth_response):
        """
        Use the access_token to get the user's info.

        :param token_type: the token type returned from step 2.
        :param access_token: the access token returned from step 2.
        :return: the users's info.
        """
        if 'access_token' in auth_response:
            access_token = auth_response['access_token']
            if isinstance(access_token, list):
                access_token = auth_response['access_token'][0]

            params = {'access_token': access_token}
            try:
                response = requests.get(self.user_info_url, params=params)
                json = response.json()
                return self.request_user_info(access_token, json)
            except ValueError as e:
                return {'error': e.message}
        return auth_response


class OAuthUser:
    def __init__(self, access_token, service_name, service_user_id, user_name, email):
        self.access_token = access_token
        self.service_name = service_name
        self.service_user_id = service_user_id
        self.user_name = user_name
        self.email = email


class OAuthConfigException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)