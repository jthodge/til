from datasette import Response, hookimpl


@hookimpl
def register_routes() -> tuple:
    return (
        (
            r"^/til/til/(?P<topic>[^_]+)_(?P<slug>[^\.]+)\.md$",
            lambda request: Response.redirect(
                "/{topic}/{slug}".format(**request.url_vars), status=301
            ),
        ),
    )
