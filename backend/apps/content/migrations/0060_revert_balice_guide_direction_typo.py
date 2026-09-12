"""The client edited the Round-12 comprehensive guide's PL slug/title/
seo_title in Django Admin, changing "z lotniska" (FROM the airport) to
"na lotnisko" (TO the airport), believing "z lotniska" was a grammar
mistake. It wasn't: "z lotniska" (z + genitive) and "na lotnisko" (na +
accusative) are both grammatically correct Polish — they just mean
opposite things.

This matters because the guide's own body is entirely about being picked
up FROM the airport (flight monitoring, waiting in hali przylotów, driver
meets you at arrivals) — it never covers departing TO the airport. The
"na lotnisko" (to-the-airport) intent now has its own dedicated, brand
new FixedRoute + supporting blog post from this same session
(transfer-na-lotnisko-balice / ile-kosztuje-transfer-na-lotnisko-balice),
built specifically because that's a DIFFERENT, cheaper product (no flight
monitoring needed). The client's rename made this guide's title collide
with that new pair while its content still describes the old (from-
airport) product — reintroducing the exact keyword-cannibalization /
customer-confusion problem fixed in migrations 0058-0059 for balice-krakow.

Reverts PL slug/title_pl/seo_title_pl to the original "z lotniska"
wording (matches the body, matches balice-krakow's existing cross-link to
this guide, which already points at the old slug). title_en/de and
seo_title_en/de were never touched by the client's edit (English/German
"airport transfer" doesn't carry this z/na ambiguity), so nothing to
revert there.

A full frontend rebuild is still required after this deploys — the old
slug briefly 200'd with STALE pre-rename content from Next's static page
cache (this project's known "stale generateStaticParams page" gotcha,
see prior rounds) even after the client's admin edit had already taken
effect in the database.
"""

from django.db import migrations

OLD_SLUG = "transfer-na-lotnisko-krakow-balice-kompletny-przewodnik-2026"
NEW_SLUG = "transfer-z-lotniska-krakow-balice-kompletny-przewodnik-2026"

RESTORED_TITLE_PL = "Transfer z lotniska Kraków Balice: kompletny przewodnik 2026"
RESTORED_SEO_TITLE_PL = "Transfer z lotniska Kraków Balice — przewodnik 2026 | transfer247.pl"

WRONG_TITLE_PL = "Transfer na lotnisko Kraków Balice: kompletny przewodnik 2026"
WRONG_SEO_TITLE_PL = "Transfer na lotnisko Kraków Balice — przewodnik 2026 | transfer247.pl"


def forward(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    try:
        post = BlogPost.objects.get(slug=OLD_SLUG)
    except BlogPost.DoesNotExist:
        return
    post.slug = NEW_SLUG
    post.title_pl = RESTORED_TITLE_PL
    post.seo_title_pl = RESTORED_SEO_TITLE_PL
    post.save(update_fields=["slug", "title_pl", "seo_title_pl"])


def backward(apps, schema_editor):
    BlogPost = apps.get_model("content", "BlogPost")
    try:
        post = BlogPost.objects.get(slug=NEW_SLUG)
    except BlogPost.DoesNotExist:
        return
    post.slug = OLD_SLUG
    post.title_pl = WRONG_TITLE_PL
    post.seo_title_pl = WRONG_SEO_TITLE_PL
    post.save(update_fields=["slug", "title_pl", "seo_title_pl"])


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0059_balice_krakow_faq_disambiguation_fix"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
