from application import application
from application.auth.views import login, authorized, logout, profile, user_level

__author__ = 'Chris'

application.add_url_rule('/login', view_func=login, methods=['GET'])
application.add_url_rule('/login/<service>', view_func=login, methods=['GET'])
application.add_url_rule('/authorized/<service>', view_func=authorized, methods=['GET'])
application.add_url_rule('/logout', view_func=logout, methods=['GET'])
application.add_url_rule('/profile/', view_func=profile, methods=['GET'])
application.add_url_rule('/profile/<id>', view_func=profile, methods=['GET','POST'])
application.add_url_rule('/user_level', view_func=user_level, methods=['GET'])