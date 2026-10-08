import re
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.content.models import BlogPost, ContentPage, ServicePage, ServicePricingOption
from apps.content.revalidation import flush_now
from apps.content.seed.transport_blog import ARTICLES
from apps.content.seed.transport_pages import (
    CATEGORY,
    CATEGORY_PRICING,
    CROSS_LINKS,
    MOVE,
    MOVE_SLUG,
    CATEGORY_SLUG,
)

SITE = "dowieziemycie"
PLACEHOLDER_RE = re.compile(r"\[(?:DO POTWIERDZENIA|DO WERYFIKACJI PRAWNEJ|TREŚĆ)[^\]]*\]")
BLOG_FIELDS = [
    "tag_pl", "tag_en", "title_pl", "title_en", "excerpt_pl", "excerpt_en", "body_pl", "body_en",
    "seo_title_pl", "seo_title_en", "seo_description_pl", "seo_description_en",
]


class Command(BaseCommand):
    help = (
        "Loads the 'Transport rzeczy' category (dowieziemycie.pl): category page, small-move subpage, pricing "
        "options and five blog articles — all as unpublished drafts. Idempotent: existing objects are left "
        "alone (owner edits survive) unless --force. --publish makes everything live together and links the "
        "existing pages to it, but refuses while any [DO POTWIERDZENIA …] placeholder is left. --report lists "
        "the placeholders and the SEO title/description lengths."
    )

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Overwrite existing objects with the seed text.")
        parser.add_argument("--publish", action="store_true", help="Publish pages + articles, add cross-links.")
        parser.add_argument("--report", action="store_true", help="Print placeholders and SEO lengths only.")

    def handle(self, *args, force, publish, report, **options):
        if report:
            return self.report()
        with transaction.atomic():
            self.load(force)
            if publish:
                self.publish()
        flush_now()

    # --- loading ---------------------------------------------------------------

    def _upsert(self, model, lookup, values, force):
        obj = model.objects.filter(**lookup).first()
        if obj is None:
            obj = model.objects.create(**lookup, **values)
            self.stdout.write(self.style.SUCCESS(f"+ {model.__name__} {lookup}"))
        elif force:
            for field, value in values.items():
                setattr(obj, field, value)
            obj.save()
            self.stdout.write(self.style.WARNING(f"~ {model.__name__} {lookup} (overwritten)"))
        else:
            self.stdout.write(f"= {model.__name__} {lookup} (exists, left as is)")
        return obj

    def load(self, force):
        def page_values(data, parent):
            values = {k: v for k, v in data.items() if k != "slug"}
            return {**values, "site": SITE, "parent": parent}

        category = self._upsert(ServicePage, {"slug": CATEGORY_SLUG}, page_values(CATEGORY, None), force)
        self._upsert(ServicePage, {"slug": MOVE_SLUG}, page_values(MOVE, category), force)
        for option in CATEGORY_PRICING:
            values = {k: v for k, v in option.items() if k != "code"}
            self._upsert(ServicePricingOption, {"page": category, "code": option["code"]}, values, force)
        for article in ARTICLES:
            values = {field: article[field] for field in BLOG_FIELDS}
            values.update(site=SITE, is_published=False, published_at=date.today())
            self._upsert(BlogPost, {"slug": article["slug"]}, values, force)

    # --- publishing ------------------------------------------------------------

    def _seeded_objects(self):
        pages = list(ServicePage.objects.filter(slug__in=[CATEGORY_SLUG, MOVE_SLUG]))
        options = list(ServicePricingOption.objects.filter(page__slug=CATEGORY_SLUG))
        posts = list(BlogPost.objects.filter(slug__in=[a["slug"] for a in ARTICLES]))
        return pages, options, posts

    def _placeholders(self):
        found = []
        pages, options, posts = self._seeded_objects()
        for obj in [*pages, *options, *posts]:
            for field in obj._meta.get_fields():
                value = getattr(obj, field.name, None) if getattr(field, "concrete", False) else None
                if isinstance(value, str):
                    for match in PLACEHOLDER_RE.findall(value):
                        found.append((obj, field.name, match))
        return found

    def publish(self):
        placeholders = self._placeholders()
        if placeholders:
            lines = "\n".join(f"  {type(o).__name__} '{o}' · {f}: {m}" for o, f, m in placeholders)
            raise CommandError(f"Nie publikuję — zostało {len(placeholders)} placeholderów:\n{lines}")

        pages, _, posts = self._seeded_objects()
        for page in pages:
            page.is_published = True
            page.save()
        for post in posts:
            if not post.is_published:
                post.is_published, post.published_at = True, date.today()
                post.save()
        for slug, field, marker, text, before in CROSS_LINKS:
            self._add_cross_link(slug, field, marker, text, before)
        self.stdout.write(self.style.SUCCESS("Opublikowano kategorię, podstronę i artykuły."))

    def _add_cross_link(self, slug, field, marker, text, before):
        page = ContentPage.objects.filter(slug=slug, site=SITE).first()
        if page is None:
            return self.stdout.write(self.style.WARNING(f"! brak strony {slug} — link pominięty"))
        body = getattr(page, field) or ""
        if marker in body:
            return  # already linked
        nl = "\r\n" if "\r\n" in body else "\n"
        block = text.replace("\n", nl)
        if before and before in body:
            body = body.replace(before, f"{block}{nl}{nl}{before}", 1)
        else:
            body = f"{body.rstrip()}{nl}{nl}{block}"
        setattr(page, field, body)
        page.save()
        self.stdout.write(self.style.SUCCESS(f"+ link do /transport-rzeczy na {slug} ({field})"))

    # --- report ----------------------------------------------------------------

    def report(self):
        placeholders = self._placeholders()
        self.stdout.write(f"Placeholdery: {len(placeholders)}")
        for obj, field, match in placeholders:
            self.stdout.write(f"  {type(obj).__name__} '{obj}' · {field}: {match}")
        self.stdout.write("\nSEO (znaki):")
        pages, _, posts = self._seeded_objects()
        for obj in [*pages, *posts]:
            for lang in ("pl", "en"):
                title = getattr(obj, f"seo_title_{lang}")
                desc = getattr(obj, f"seo_description_{lang}")
                self.stdout.write(f"  {obj.slug} [{lang}] title {len(title)}: {title}")
                self.stdout.write(f"  {' ' * len(obj.slug)} [{lang}] desc  {len(desc)}: {desc}")
