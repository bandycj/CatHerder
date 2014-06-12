from functools import wraps

from flask import request, render_template


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