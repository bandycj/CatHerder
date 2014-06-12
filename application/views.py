from flask.ext.login import current_user, login_required

from common.decorators import templated

__author__ = 'Chris'


@templated
def index():
    try:
        if current_user.is_authenticated():
            return {'user': current_user}
    except:
        return {}


@templated
@login_required
def about():
    return {"value": "42"}



