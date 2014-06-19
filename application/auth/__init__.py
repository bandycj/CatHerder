from flask.ext.login import LoginManager

from application import application, models
from application.auth.oauth_classes import OAuthService
from application.models import User


__author__ = 'Chris'

import services
import routes

login_manager = LoginManager()
login_manager.init_app(app=application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-danger'

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@login_manager.token_loader
def load_token(token):
    return User.query.filter_by(auth_token=token).first() or models.AnonymousUser()

