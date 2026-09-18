# New ContentPage: "Lokalny przewóz osób" — link-audit finding (see the
# frontend commit touching pillars-section.tsx/topic-tiles-section.tsx the
# same day). The homepage's "🚐 Lokalny przewóz osób" card linked to
# "#routes", a section listing town-to-town LocalRoute pricing — not the
# same thing as a dedicated page for this whole service category (everyday
# local rides: doctor visits, station pickups, errands), which had no
# indexable page or keyword presence of its own at all before this.
#
# EN copy is a plain translation of the approved PL copy (not new claims) —
# added because ContentPage.title_en is a required field, not because EN
# was in scope for this round; the brief explicitly deferred EN wording
# decisions to a later pass.

from django.db import migrations

BODY_PL = (
    "Nie każdy wyjazd to podróż na lotnisko czy impreza w mieście. Czasem "
    "potrzebujesz po prostu dojechać do lekarza, odebrać kogoś ze szkoły, "
    "wrócić z zakupów albo złapać pociąg na dworcu — i to jest dokładnie "
    "to, do czego jesteśmy tu, na miejscu, w Rybnej i okolicy.\n\n"
    "## Do czego najczęściej nas wzywacie\n\n"
    "- Dojazd do przychodni/lekarza w Krakowie lub Czernichowie — także "
    "gdy nie prowadzisz auta albo źle się czujesz\n"
    "- Podwózka na dworzec lub przystanek, gdy rozkład jazdy nie pasuje "
    "do Twojego planu dnia\n"
    "- Powrót do domu w nocy, gdy nie ma już komunikacji miejskiej\n"
    "- Codzienny dojazd do pracy lub szkoły na stałej trasie\n"
    "- Załatwianie spraw urzędowych, zakupy, wizyty rodzinne\n\n"
    "## Jak to działa\n\n"
    "Zamawiasz online lub telefonicznie, widzisz dokładną pozycję "
    "kierowcy na mapie, płacisz z góry ustaloną, stałą cenę — bez "
    "negocjacji i niepewności, czy ktoś w ogóle przyjedzie.\n\n"
    "Obsługujemy na stałe: Rybną, Liszki, Kaszów, Czernichów, Sankę, "
    "Alwernię i Przeginię Narodową — [zobacz wszystkie obsługiwane "
    "kierunki](/kierunki).\n\n"
    "Wracasz z Krakowa późno w nocy? Sprawdź naszą [ofertę nocnego "
    "transferu](/nocny-transfer-krakow)."
)

BODY_EN = (
    "Not every trip is a flight to catch or a night out in the city. "
    "Sometimes you just need to get to the doctor, pick someone up from "
    "school, get back from shopping, or catch a train at the station — "
    "and that's exactly what we're here for, locally, in Rybna and the "
    "surrounding area.\n\n"
    "## What you call us for most often\n\n"
    "- A ride to a clinic or doctor in Kraków or Czernichów — including "
    "when you can't drive yourself or aren't feeling well\n"
    "- A lift to the train station or a bus stop when the timetable "
    "doesn't match your day\n"
    "- A ride home at night once public transport has stopped running\n"
    "- A daily commute to work or school on a fixed route\n"
    "- Errands, shopping trips, family visits, official business\n\n"
    "## How it works\n\n"
    "You book online or by phone, see the driver's exact position on the "
    "map, and pay a fixed price agreed upfront — no negotiating, no "
    "wondering whether anyone will actually show up.\n\n"
    "We serve, on a regular basis: Rybna, Liszki, Kaszów, Czernichów, "
    "Sanka, Alwernia and Przeginia Narodowa — [see all the areas we "
    "cover](/kierunki).\n\n"
    "Coming back from Kraków late at night? Check our [night transfer "
    "offer](/nocny-transfer-krakow)."
)

PAGE = dict(
    slug="lokalny-przewoz-osob",
    page_type="LOKALNY_PRZEWOZ",
    title_pl="Lokalny przewóz osób w gminie Czernichów i Liszki",
    title_en="Local passenger transport in Gmina Czernichów and Liszki",
    body_pl=BODY_PL,
    body_en=BODY_EN,
    seo_title_pl="Lokalny przewóz osób — Rybna, Czernichów, Liszki | dowieziemycie.pl",
    seo_title_en="Local passenger transport — Rybna, Czernichów, Liszki | dowieziemycie.pl",
    seo_description_pl=(
        "Codzienny dojazd do lekarza, na zakupy, do pracy czy na dworzec — lokalny transport w "
        "gminie Czernichów i Liszki, dostępny 24/7. Stała cena, rezerwacja online."
    ),
    seo_description_en=(
        "Everyday rides to the doctor, shopping, work or the train station — local transport in "
        "Gmina Czernichów and Liszki, available 24/7. Fixed price, book online."
    ),
)


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    slug = PAGE["slug"]
    defaults = {k: v for k, v in PAGE.items() if k != "slug"}
    ContentPage.objects.update_or_create(
        slug=slug, defaults={**defaults, "site": "dowieziemycie", "is_published": True},
    )


def backwards(apps, schema_editor):
    apps.get_model("content", "ContentPage").objects.filter(slug="lokalny-przewoz-osob").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0064_add_lokalny_przewoz_page_type"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
