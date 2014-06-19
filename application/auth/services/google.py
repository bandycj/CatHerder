
import requests
from werkzeug.exceptions import abort

from application.auth.oauth_classes import OAuthUser
from config.config_enums import OAuthServiceKey


def init_google(oauth_service):
    @oauth_service.access_token_requester
    def google_token_requester(access_token_url, params):
        """
        https://developers.google.com/docs/google-login/manually-build-a-login-flow/v2.0#confirm
        :param access_token_url: the url to send the access request to.
        :param params: the query parameters.
        :return: the access_token and expiration.
        """
        try:
            response = requests.post(access_token_url, data=params)
            json = response.json()
            return json
        except:
            abort(501)


    @oauth_service.user_info_requester
    def google_user_requester(access_token, json):
        """
        https://developers.google.com/docs/graph-api/reference/v2.0/user
        :param access_token: the access_token obtained in step2
        :param json: the result of the call in step3
        :return: an OAuthUser
        """
        return OAuthUser(
            access_token=access_token,
            service_name=OAuthServiceKey.GOOGLE.value,
            service_user_id=json['id'],
            user_name=json['displayName'],
            email=json['emails'][0]['value']
        )