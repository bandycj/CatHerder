from flask import request, abort, flash
from flask.ext.login import current_user, login_user, logout_user
from werkzeug.utils import redirect

from application import index_url
from application.auth.services import oauth_services
from application.models import OAuthIdentity, User
from common.decorators import templated
from config.config_enums import OAuthServiceKey


__author__ = 'Chris'


@templated
def login(service=None):
    if service is None:
        if current_user.is_authenticated():
            flash('You are already logged in as ' + current_user.name +
                  '. Clicking a link here will link that service to your '
                  'current account. You will then be able to login with either.',
                  'warning')
        return {'oauth_services': oauth_services}
    else:
        oauth_service = OAuthServiceKey(service)
        if oauth_service in oauth_services:
            return oauth_services[oauth_service].redirect_service_login()
        abort(500)


def authorized(service):
    try:
        oauth_service = OAuthServiceKey(service)
        if oauth_service in oauth_services:
            auth_response = oauth_services[oauth_service].get_access_token(request.url)
            oauth_user = oauth_services[oauth_service].get_user_info(auth_response)

            # If someone in this session is already logged in, link this auth to them.
            if current_user.is_authenticated():
                oauth_id, created = current_user.add_oauth_identity(oauth_user.service_name, oauth_user.service_user_id)
                if created:
                    flash('Linked your ' + oauth_service.value + ' account to your CatHerder account!', 'success')
                else:
                    flash('Your ' + oauth_service.value + ' account was already linked to your CatHerder account.', 'success')
            else:
                # First try to look them up by their oauth service id.
                user = OAuthIdentity.get_user(oauth_user.service_name, oauth_user.service_user_id)
                if user is None:
                    # So we don't know about this social login yet, see if we have their email.
                    user, created = User.add_user(
                        name=oauth_user.user_name,
                        email=oauth_user.email,
                        oauth_service_name=oauth_service.value,
                        oauth_service_id=oauth_user.service_user_id
                    )
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