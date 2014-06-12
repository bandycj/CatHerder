from flask import Flask, url_for
from flask.ext.login import LoginManager


application = Flask(__name__)
application.config.from_envvar('CATHERDER_CONFIG')

import models
login_manager = LoginManager()
login_manager.init_app(app=application)

import routes
from application.views import index
index_url = lambda: url_for(index.__name__)

from application import auth

@login_manager.user_loader
def load_user(id):
    print '<<<load user'
    return models.User.query.get(id)

@login_manager.token_loader
def load_token(token):
    print '<<<load token'
    user = models.User.get_user(auth_token=token)
    if user:
        return user
    return models.AnonymousUser()