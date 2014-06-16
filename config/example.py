import os

from config.config_enums import OAuthServiceKey, ConfigKey


__author__ = 'Chris'

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable cross site request forgery protection for forms.
CSRF_ENABLED = True

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# http://clsc.net/tools-old/random-string-generator.php
SECRET_KEY = '<super secret key>'
SERVER_NAME = '127.0.0.1:5510'

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../database.db')
DEFAULT_USER_LEVEL = 'user'
ADMIN_USER_LEVEL = 'admin'
USER_LEVELS = [ADMIN_USER_LEVEL, DEFAULT_USER_LEVEL]

OAUTH_CONFIG = {
    OAuthServiceKey.GOOGLE: {
        ConfigKey.SERVICE_LOGIN_URL: 'https://accounts.google.com/o/oauth2/auth',
        ConfigKey.ACCESS_TOKEN_URL: 'https://accounts.google.com/o/oauth2/token',
        ConfigKey.USER_INFO_URL: 'https://www.googleapis.com/plus/v1/people/me',
        ConfigKey.CLIENT_ID: '<google client id>',
        ConfigKey.CLIENT_SECRET: '<google client secret>'
    },
    OAuthServiceKey.FACEBOOK: {
        ConfigKey.SERVICE_LOGIN_URL: 'https://www.facebook.com/dialog/oauth',
        ConfigKey.ACCESS_TOKEN_URL: 'https://graph.facebook.com/oauth/access_token',
        ConfigKey.USER_INFO_URL: 'https://graph.facebook.com/me',
        ConfigKey.CLIENT_ID: '<facebook app id>',
        ConfigKey.CLIENT_SECRET: '<facebook app secret>',
    }
}