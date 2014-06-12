from application import application

from application.auth.oauth_classes import OAuthService

__author__ = 'Chris'

oauth_services = {}
for service in application.config['OAUTH_CONFIG']:
    oauth_services[service] = OAuthService(service)

from application.auth.views import login, authorized, logout
from application.auth.services import facebook, google
import routes