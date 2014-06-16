from flask import request
from flask.ext.login import current_user, login_user

from application.auth.services import oauth_services
from application.models import OAuthIdentity, User
from config.config_enums import OAuthServiceKey


__author__ = 'Chris'


def auth_user(service):
    try:
        oauth_service = OAuthServiceKey(service)
        if oauth_service in oauth_services:
            auth_response = oauth_services[oauth_service].get_access_token(request.url)
            oauth_user = oauth_services[oauth_service].get_user_info(auth_response)

            if current_user.is_authenticated():
                return already_logged_in(oauth_user, oauth_service)
            else:
                return perform_login(oauth_user, oauth_service)
    except ValueError as e:
        return None, e.message, False


def already_logged_in(oauth_user, oauth_service):
    """
    If a user is already logged in, attempt to link this new social id to their existing user account.
    :param oauth_user: the OAuthUser returned from the OAuth handshake.
    :param oauth_service: the OAuthService descriptor.
    :return: User or None, message as string, success as boolean.
    """
    try:
        oauth_id, created = current_user.add_oauth_identity(oauth_user.service_name, oauth_user.service_user_id)
        if created:
            message = 'Linked your ' + oauth_service.value + ' account to your CatHerder account!'
        else:
            message = 'Your ' + oauth_service.value + ' account was already linked to your CatHerder account.'
        return current_user, message, True
    except Exception as e:
        return None, e.message, False


def perform_login(oauth_user, oauth_service):
    """
    Attempts to lookup a user and creates one if it couldn't find one. Then performs login_user().
    :param oauth_user: the OAuthUser returned from the OAuth handshake.
    :param oauth_service: the OAuthService descriptor.
    :return: User or None, message as string, success as boolean.
    """
    try:
        # First try to look them up by their oauth service id.
        user = OAuthIdentity.get_user(oauth_user.service_name, oauth_user.service_user_id)
        if user is None:
            # So we don't know about this social login yet, see if we can find them by name/email
            user, created = User.add_user(
                name=oauth_user.user_name,
                email=oauth_user.email,
                oauth_service_name=oauth_service.value,
                oauth_service_id=oauth_user.service_user_id
            )

        login_user(user, remember=True)
        message = 'You are now logged in with %s' % (oauth_service.value)
        return user, message, True
    except Exception as e:
        return None, e.message, False

