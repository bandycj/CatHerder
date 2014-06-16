from flask import Flask
from flask.ext.wtf import CsrfProtect


application = Flask(__name__)
application.config.from_envvar('CATHERDER_CONFIG')
CsrfProtect(application)
import models
import routes

from application import auth