from .sites import DEFAULT_SITE, VALID_SITE_CODES


class SiteMiddleware:
    """Reads the X-Site header each frontend sends and attaches the resolved
    code as request.site_code — falls back to the default (dowieziemycie)
    for any request that doesn't send it or sends something unrecognized,
    so the existing frontend keeps working without changes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site = request.headers.get("X-Site")
        request.site_code = site if site in VALID_SITE_CODES else DEFAULT_SITE
        return self.get_response(request)
