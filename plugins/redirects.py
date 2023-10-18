from datasette import hookimpl
from datasette.utils.asgi import Response


@hookimpl
def register_routes():
    return (
        (
            r"^/til/til/(?P<topic>[^_]+)_(?P<slug>[^\.]+)\.md$",
            lambda request: Response.redirect(
                "/{topic}/{slug}".format(**request.url_vars), status=301
            ),
        ),
    )