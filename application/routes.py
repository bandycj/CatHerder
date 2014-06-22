from application import application
from application.views import index, about, admin

__author__ = 'Chris'

application.add_url_rule('/', view_func=index, methods=['GET'])
application.add_url_rule('/about', view_func=about, methods=['GET'])
application.add_url_rule('/admin', view_func=admin, methods=['GET'])