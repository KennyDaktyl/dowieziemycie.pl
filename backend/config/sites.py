"""The two brands sharing this backend. A `site` field (using SITE_CHOICES)
on content/booking models scopes what belongs to which frontend; SiteMiddleware
(see middleware.py) reads which one a request is for from the X-Site header
each frontend sends, defaulting to dowieziemycie for anything that doesn't
(keeps the existing frontend working without needing to send it)."""

SITE_DOWIEZIEMYCIE = "dowieziemycie"
SITE_TRANSFER247 = "transfer247"

SITE_CHOICES = [
    (SITE_DOWIEZIEMYCIE, "dowieziemycie.pl"),
    (SITE_TRANSFER247, "transfer247.pl"),
]

DEFAULT_SITE = SITE_DOWIEZIEMYCIE

VALID_SITE_CODES = {code for code, _ in SITE_CHOICES}

# Used to brand outgoing SMS text ("dowieziemycie.pl - Twoj kod: ...") since
# the two frontends share one SMSAPI account/sender for now.
SITE_DISPLAY_NAMES = dict(SITE_CHOICES)
