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

# Used to brand outgoing SMS text ("transfer247 - Twoj kod: ...") — no ".pl"
# suffix on purpose: SMSAPI's spam filter (error 94, "not allowed to send
# messages with link") rejects any text that looks like a domain name, and
# both "dowieziemycie.pl" and "transfer247.pl" match that pattern.
SITE_DISPLAY_NAMES = {
    SITE_DOWIEZIEMYCIE: "dowieziemycie",
    SITE_TRANSFER247: "transfer247",
}

# The public frontend each brand's outgoing links (emails, etc.) should
# point back to.
SITE_URLS = {
    SITE_DOWIEZIEMYCIE: "https://dowieziemycie.pl",
    SITE_TRANSFER247: "https://transfer247.pl",
}
