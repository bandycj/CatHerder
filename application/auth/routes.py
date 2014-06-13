from application import application
from application.auth.views import login, authorized, logout

__author__ = 'Chris'

application.add_url_rule('/login', view_func=login, methods=['GET'])
application.add_url_rule('/login/<service>', view_func=login, methods=['GET'])
application.add_url_rule('/authorized/<service>', view_func=authorized, methods=['GET'])
application.add_url_rule('/logout', view_func=logout, methods=['GET'])