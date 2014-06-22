from flask import abort, flash, url_for, request, jsonify, render_template
from flask.ext.login import current_user, logout_user, login_required
from flask.ext.wtf import Form
from werkzeug.utils import redirect
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email

from application.auth.controller import auth_user
from application.auth.services import oauth_services
from application.models import User, save, UserLevel, rollback, admin_user_level
from common.decorators import templated, admin_required
from config.config_enums import OAuthServiceKey


__author__ = 'Chris'


class ProfileForm(Form):
    name = StringField('User Name', validators=[DataRequired()], )
    email = EmailField('Email', validators=[DataRequired(), Email()])


json_error = lambda errors: jsonify(message=errors, message_class='danger')
json_success = lambda: jsonify(message='Success', message_class='success')


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


@login_required
def profile(id=None):
    if id is not None:
        user = User.query.get_or_404(id)
    else:
        user = current_user

    form = ProfileForm(obj=user)
    can_edit = current_user.id == int(id) or current_user.is_admin()
    if can_edit and request.method == 'POST':
        if form.validate_on_submit():
            try:
                form.populate_obj(user)
                save()
                return json_success()
            except Exception as e:
                return json_error(e.message)
        else:
            return json_error('Invalid data entered.')
    else:
        return render_template('profile.html',
                               user=user,
                               oauth_services=oauth_services,
                               can_edit=can_edit,
                               form=form
        )


@admin_required
def user_level():
    user_id = request.args.get('userId', -1, type=int)
    user_level_id = request.args.get('userLevelId', -1, type=int)
    try:
        user = User.query.get_or_404(user_id)
        user_level = UserLevel.query.get_or_404(user_level_id)
        admin = admin_user_level()
        if user.user_level == admin and admin.users.count() < 2:
            return json_error('You can not remove the last admin!')
        elif user.user_level == admin and user == current_user:
            return json_error('You can not demote yourself from admin!')
        else:
            user.user_level_id = user_level.id
            save()
            return json_success()
    except Exception as e:
        rollback()
        return json_error(e.message)