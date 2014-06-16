from flask.ext.login import LoginManager

from application import application, models
from application.auth.oauth_classes import OAuthService


__author__ = 'Chris'

import services
import routes

login_manager = LoginManager()
login_manager.init_app(app=application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'alert-danger'

@login_manager.user_loader
def load_user(id):
    return models.User.query.get(id)


@login_manager.token_loader
def load_token(token):
    user = models.User.get_user(auth_token=token)
    if user:
        return user
    return models.AnonymousUser()

