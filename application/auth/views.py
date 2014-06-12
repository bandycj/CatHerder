from flask import request, abort, flash
from flask.ext.login import current_user, login_user, logout_user
from werkzeug.utils import redirect

from application import index_url
from application.auth import oauth_services
from application.models import OAuthIdentity, User
from common.decorators import templated
from config.config_enums import OAuthService


__author__ = 'Chris'


@templated
def login(service=None):
    if service is None:
        if current_user.is_authenticated():
            return redirect(index_url())
        else:
            return {'oauth_services': oauth_services}
    else:
        oauth_service = OAuthService(service)
        if oauth_service in oauth_services:
            return oauth_services[oauth_service].redirect_service_login()
        else:
            abort(500)


def authorized(service):
    try:
        oauth_service = OAuthService(service)
        if oauth_service in oauth_services:
            auth_response = oauth_services[oauth_service].get_access_token(request.url)
            oauth_user = oauth_services[oauth_service].get_user_info(auth_response)
            # First try to look them up by their oauth service id.
            user = OAuthIdentity.get_user(oauth_user.service_name, oauth_user.service_user_id)
            if user is None:
                # Now try less secure means
                user = User.get_user(email=oauth_user.email)
                if user is None:
                    user = User.add_user(
                        user_name=oauth_user.user_name,
                        email=oauth_user.email,
                        oauth_service_name=oauth_service.value,
                        oauth_service_id=oauth_user.service_user_id
                    )
                else:
                    # If we found the user by email but not oauth_identity then add a new identity.
                    user.add_oauth_identity(oauth_user.service_name, oauth_user.service_user_id)

            if user is not None:
                login_user(user, remember=True)
                flash('You are now logged in with %s' % (oauth_service.value), category='info')
            return redirect(index_url())
    except ValueError as e:
        print e.message
    abort(500)


def logout():
    if current_user.is_authenticated():
        logout_user()
        flash('Logout complete!', category='info')
    else:
        flash('You are not logged in.', category='error')
    return redirect(index_url())