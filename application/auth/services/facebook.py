import urlparse

import requests

from application.auth import oauth_services
from application.auth.oauth_classes import OAuthUser
from config.config_enums import OAuthService

facebook = oauth_services[OAuthService.FACEBOOK]


@facebook.access_token_requester
def facebook_token_requester(access_token_url, params):
    """
    https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/v2.0#confirm
    :param access_token_url: the url to send the access request to.
    :param params: the query parameters.
    :return: the access_token and expiration.
    """
    response = requests.get(access_token_url, params=params)
    return urlparse.parse_qs(response.text)


@facebook.user_info_requester
def facebook_user_requester(access_token, json):
    """
    https://developers.facebook.com/docs/graph-api/reference/v2.0/user
    :param access_token: the access_token obtained in step2
    :param json: the result of the call in step3
    :return: an OAuthUser
    """
    return OAuthUser(
        access_token=access_token,
        service_name='google',
        service_user_id=json['id'],
        user_name=json['first_name'],
        email=json['email']
    )