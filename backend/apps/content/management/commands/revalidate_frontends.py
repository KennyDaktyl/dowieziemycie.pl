from django.core.management.base import BaseCommand, CommandError

from apps.content.revalidation import all_tags, send
from config.sites import VALID_SITE_CODES


class Command(BaseCommand):
    help = (
        "Revalidates the frontends' cache — every tag by default. Run after a "
        "deploy with data migrations: migrations use historical models, which "
        "don't fire the post_save signals that revalidate on Admin edits."
    )

    def add_arguments(self, parser):
        parser.add_argument("tags", nargs="*", help="Tags to revalidate (default: all).")
        parser.add_argument("--site", choices=sorted(VALID_SITE_CODES), help="Only this brand (default: both).")

    def handle(self, *args, tags, site, **options):
        tags = tags or all_tags()
        failed = []
        for code in [site] if site else sorted(VALID_SITE_CODES):
            if send(code, tags, timeout=15):
                self.stdout.write(self.style.SUCCESS(f"{code}: {', '.join(tags)}"))
            else:
                failed.append(code)
        if failed:
            raise CommandError(f"Revalidation failed or not configured for: {', '.join(failed)}")
