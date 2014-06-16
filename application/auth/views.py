from flask import abort, flash, url_for, request
from flask.ext.login import current_user, logout_user, login_required
from flask.ext.wtf import Form
from werkzeug.utils import redirect
from wtforms.ext.sqlalchemy.orm import model_form

from application.auth.controller import auth_user
from application.auth.services import oauth_services
from application.models import User, save
from common.decorators import templated
from config.config_enums import OAuthServiceKey


__author__ = 'Chris'
ProfileForm = model_form(User, Form)


@templated
def login(service=None):
    if service is None:
        if current_user.is_authenticated():
            flash('You are already logged in as ' + current_user.name +
                  '. Clicking a link here will link that service to your '
                  'current account. You will then be able to login with either.',
                  'alert-info')
        return {'oauth_services': oauth_services}
    else:
        oauth_service = OAuthServiceKey(service)
        if oauth_service in oauth_services:
            return oauth_services[oauth_service].redirect_service_login()
        abort(500)


def authorized(service):
    user, message, success = auth_user(service)
    if success:
        flash(message, 'alert-success')
    else:
        flash(message, 'alert-danger')
    return request.values.get('next') or redirect(url_for('index'))


def logout():
    if current_user.is_authenticated():
        logout_user()
        flash('Logout complete!', category='alert-success')
    else:
        flash('You are not logged in.', category='alert-danger')
    return request.values.get('next') or redirect(url_for('index'))


@templated
@login_required
def profile(id=None):
    if id is not None:
        user = User.query.get(id)
    else:
        user = current_user
    can_edit = current_user.id == id or current_user.is_admin()
    return {'user': user,
            'oauth_services': oauth_services,
            'can_edit': can_edit}


# TODO: enable profile editing.
    
# @templated
# @login_required
# def profile_edit(id):
#     if current_user.id == id or current_user.is_admin():
#         user = User.query.get(id)
#         form = ProfileForm(request.form, user)
#         if  request.method == 'POST' and form.validate_on_submit():
#             form.populate_obj(user)
#             save()
#             flash('Profile Updated!', 'alert-success')
#             return redirect(url_for('profile', id=id))
#         return {'form': form}
#     else:
#         abort(401)