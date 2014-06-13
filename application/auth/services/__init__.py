from application import application
from application.auth import OAuthService
from application.auth.services.facebook import init_facebook
from application.auth.services.google import init_google
from config.config_enums import OAuthServiceKey

__author__ = 'Chris'

oauth_services = {}
for service in application.config['OAUTH_CONFIG']:
    oauth_service = OAuthService(service)
    if service is OAuthServiceKey.GOOGLE:
        init_google(oauth_service)
    elif service is OAuthServiceKey.FACEBOOK:
        init_facebook(oauth_service)

    oauth_services[service] = oauth_service