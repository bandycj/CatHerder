from functools import wraps

from flask import request, render_template, current_app, flash, redirect, url_for
from flask.ext.login import current_user


__author__ = 'Chris'


def templated(f, template=None):
    """
    If no template name is provided it will use the endpoint of the URL map with dots converted to slashes + '.html'.
    Otherwise the provided template name is used. When the decorated function returns, the dictionary returned is passed
    to the template rendering function. If None is returned, an empty dictionary is assumed, if something else than a
    dictionary is returned we return it from the function unchanged.

    :param template: optional template file name.
    :return: the decorated function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        template_name = template
        if template_name is None:
            template_name = request.endpoint.replace('.', '/') + '.html'
        ctx = f(*args, **kwargs)
        if ctx is None:
            ctx = {}
        elif not isinstance(ctx, dict):
            return ctx
        return render_template(template_name, **ctx)

    return decorated_function


def admin_required(func):
    '''
    If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated and is an admin before calling the actual view.
    (If they are not, it calls the :attr:`LoginManager.unauthorized` callback.)
    :param func: The view function to decorate.
    :type func: function
    '''
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated() or not current_user.is_admin():
            flash('You do not have permission to access this function.', 'alert-danger')
            return request.values.get('next') or redirect(url_for('index'))
        return func(*args, **kwargs)
    return decorated_view