"""Branded HTML wrapper for customer-facing emails — every transactional
email is also the one piece of marketing a customer reliably opens, so it
carries the brand's look and a link back to the site rather than being bare
text. Dispatcher-facing emails (internal ops, not customer marketing) stay
plain text and don't go through this."""

from django.template.loader import render_to_string

from config.sites import SITE_DOWIEZIEMYCIE, SITE_TRANSFER247, SITE_URLS

_BRANDING = {
    SITE_DOWIEZIEMYCIE: {
        "logo_text": "dowieziemycie.pl",
        "tagline": "Twój sąsiad z busem",
        "bg_color": "#0b0f16",
        "panel_color": "#121a24",
        "text_color": "#edeef2",
        "muted_color": "#8b96a3",
        "accent_color": "#f5a623",
        "accent_text_color": "#1a1206",
    },
    SITE_TRANSFER247: {
        "logo_text": "transfer247.pl",
        "tagline": "Transfery lotniskowe bez stresu",
        "bg_color": "#f4f2ef",
        "panel_color": "#ffffff",
        "text_color": "#2c2116",
        "muted_color": "#75695c",
        "accent_color": "#c1552c",
        "accent_text_color": "#ffffff",
    },
}


def render_customer_email_html(site: str, heading: str, body_lines: list[str], cta_label: str = "", cta_url: str = "") -> str:
    branding = _BRANDING[site]
    site_url = SITE_URLS[site]
    return render_to_string("emails/customer_email.html", {
        **branding,
        "site_url": site_url,
        "site_url_display": site_url.removeprefix("https://"),
        "heading": heading,
        "body_lines": body_lines,
        "cta_label": cta_label,
        "cta_url": cta_url,
    })
