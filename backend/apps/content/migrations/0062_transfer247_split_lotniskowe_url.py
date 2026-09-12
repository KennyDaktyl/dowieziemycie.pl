"""Split the /transfery URL into two distinct sections, per the client's
SEO request: "lotniskowe" is a strong, high-volume keyword and deserves its
own URL segment (transfer247.pl/transfery-lotniskowe/...) instead of living
as an anchored section inside the generic /transfery page. This reverses a
deliberate decision from an earlier round (which chose a category field
over separate URLs specifically to avoid a slug migration) — the client
now explicitly wants the URL split for topical relevance, so this migration
does it carefully with redirects (added on the frontend) rather than just
breaking the old URLs.

Two things happen here on the data side (the frontend routing/redirect
split lives in the transfer247.pl repo, not this migration):

1. `FixedRoute.category` DWORZEC_PKP -> TRANSFER for existing rows (the
   "Dworzec PKP" framing was itself a complaint — the client wants to add
   plain one-way transfers like "Kraków -> Energylandia" under this
   category without every one having to originate at the train station).
   Individual route slugs/names are untouched (dworzec-energylandia,
   dworzec-balice keep their accurate, specific names — only the umbrella
   category/menu label changes).

2. Every internal link from a FixedRoute/BlogPost body (site=transfer247)
   or BlogPostLink.url that points at a LOTNISKO-category route under the
   old /transfery/<slug> path gets rewritten to /transfery-lotniskowe/<slug>
   — computed fresh from the current LOTNISKO slug set, not a hardcoded
   list, so it catches every reference including ones in posts this
   project didn't touch this session (closest-airport-to-auschwitz,
   krakow-airport-transfer-to-hotel-guide, balice-zakopane-ile-kosztuje,
   katowice-pyrzowice-jak-dojechac-do-krakowa — found by scanning prod
   before writing this). The frontend still 308-redirects any remaining
   /transfery/<lotnisko-slug> hit (external backlinks, browser bookmarks,
   search engine cache) to the new path, but internal links should point
   straight at the canonical URL rather than ride a redirect.

Idempotent (regex substitution is a no-op once already rewritten) and
reversible.
"""

import re

from django.db import migrations

SITE = "transfer247"
OLD_CATEGORY = "DWORZEC_PKP"
NEW_CATEGORY = "TRANSFER"


def _link_patterns(slugs):
    """One compiled (forward, backward) regex pair per slug, anchored on
    the markdown link parens so `/transfery/balice-krakow` can never
    accidentally match as a substring of some other, longer slug."""
    pairs = []
    for slug in slugs:
        escaped = re.escape(slug)
        forward = re.compile(r"\(/transfery/" + escaped + r"\)")
        backward = re.compile(r"\(/transfery-lotniskowe/" + escaped + r"\)")
        pairs.append((slug, forward, backward))
    return pairs


def _rewrite_bodies(FixedRoute, BlogPost, patterns, forward):
    fields = ["body_pl", "body_en", "body_de"]

    for model in (FixedRoute, BlogPost):
        for obj in model.objects.filter(site=SITE):
            changed = []
            for field in fields:
                text = getattr(obj, field) or ""
                new_text = text
                for slug, fwd_re, back_re in patterns:
                    if forward:
                        new_text = fwd_re.sub(f"(/transfery-lotniskowe/{slug})", new_text)
                    else:
                        new_text = back_re.sub(f"(/transfery/{slug})", new_text)
                if new_text != text:
                    setattr(obj, field, new_text)
                    changed.append(field)
            if changed:
                obj.save(update_fields=changed)


def _rewrite_links(BlogPostLink, slugs, forward):
    qs = BlogPostLink.objects.filter(post__site=SITE)
    for link in qs:
        for slug in slugs:
            old = f"/transfery/{slug}"
            new = f"/transfery-lotniskowe/{slug}"
            if forward and link.url == old:
                link.url = new
                link.save(update_fields=["url"])
            elif not forward and link.url == new:
                link.url = old
                link.save(update_fields=["url"])


def forward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    BlogPost = apps.get_model("content", "BlogPost")
    BlogPostLink = apps.get_model("content", "BlogPostLink")

    FixedRoute.objects.filter(site=SITE, category=OLD_CATEGORY).update(category=NEW_CATEGORY)

    lotnisko_slugs = list(
        FixedRoute.objects.filter(site=SITE, category="LOTNISKO").values_list("slug", flat=True)
    )
    patterns = _link_patterns(lotnisko_slugs)
    _rewrite_bodies(FixedRoute, BlogPost, patterns, forward=True)
    _rewrite_links(BlogPostLink, lotnisko_slugs, forward=True)


def backward(apps, schema_editor):
    FixedRoute = apps.get_model("content", "FixedRoute")
    BlogPost = apps.get_model("content", "BlogPost")
    BlogPostLink = apps.get_model("content", "BlogPostLink")

    lotnisko_slugs = list(
        FixedRoute.objects.filter(site=SITE, category="LOTNISKO").values_list("slug", flat=True)
    )
    patterns = _link_patterns(lotnisko_slugs)
    _rewrite_bodies(FixedRoute, BlogPost, patterns, forward=False)
    _rewrite_links(BlogPostLink, lotnisko_slugs, forward=False)

    FixedRoute.objects.filter(site=SITE, category=NEW_CATEGORY).update(category=OLD_CATEGORY)


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0061_transfer247_rename_dworzec_pkp_category"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
