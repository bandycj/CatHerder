from flask.ext.login import current_user, login_required

from application.models import User, UserLevel

from common.decorators import templated, admin_required


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


@templated
@admin_required
def admin():
    return {
        'users': User.query.all(),
        'user_levels': UserLevel.query.all()
    }
