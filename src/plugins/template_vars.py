import html

from datasette import hookimpl


def highlight(s: str) -> str:
    s = html.escape(s)
    return s.replace("b4de2a49c8", "<strong>").replace("8c94a2ed4b", "</strong>")


@hookimpl
def extra_template_vars(request: object) -> dict:
    return {
        "q": getattr(request, "args", {}).get("q", ""),
        "highlight": highlight,
    }
