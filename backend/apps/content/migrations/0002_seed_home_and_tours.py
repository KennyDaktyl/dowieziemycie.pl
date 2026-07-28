# Seeds the homepage hero copy and the 3 tour offers from the design
# reference (docs/landing-page-brief.md), in PL and EN.

from django.db import migrations

TOURS = [
    dict(
        slug="auschwitz",
        title_pl="Auschwitz-Birkenau",
        title_en="Auschwitz-Birkenau",
        summary_pl="Transfer i powrót, czas na zwiedzanie w Twoim tempie.",
        summary_en="Round-trip transfer, with time to visit at your own pace.",
        price_from=320,
        order=0,
    ),
    dict(
        slug="wieliczka",
        title_pl="Kopalnia Wieliczka",
        title_en="Wieliczka Salt Mine",
        summary_pl="Bez kolejek w busie — dojazd prosto pod wejście.",
        summary_en="Skip the queues — dropped off right at the entrance.",
        price_from=190,
        order=1,
    ),
    dict(
        slug="zakopane",
        title_pl="Zakopane",
        title_en="Zakopane",
        summary_pl="Jeden dzień w Tatrach, bez pilnowania rozkładu autokaru.",
        summary_en="A full day in the Tatra Mountains, no coach timetable to watch.",
        price_from=480,
        order=2,
    ),
]


def seed(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.update_or_create(
        pk=1,
        defaults=dict(
            eyebrow_pl="24/7 · Bezpiecznie, komfortowo, o każdej porze",
            eyebrow_en="24/7 · Safe, comfortable, any time of day",
            headline_pl="Bezpieczny przejazd. Każdej {highlight}",
            headline_en="A safe ride. Any {highlight}",
            headline_highlight_pl="pory.",
            headline_highlight_en="time.",
            lead_pl=(
                "Kraków–Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. "
                "Komfortowy, bezpieczny przejazd 24 godziny na dobę — także w nocy i w niedziele. "
                "Zarezerwuj z wyprzedzeniem dla najlepszej ceny, albo zadzwoń w dowolnej chwili — "
                "dojedziemy, tylko drożej niż przy wcześniejszej rezerwacji."
            ),
            lead_en=(
                "Kraków–Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia, Przeginia Narodowa. "
                "A comfortable, safe ride around the clock — including nights and Sundays. Book "
                "ahead for the best price, or call any time — we'll still get you there, just at "
                "a higher on-demand rate."
            ),
            footnote_pl="Zarezerwuj wcześniej — zapłacisz mniej niż za kurs na już.",
            footnote_en="Book ahead — pay less than an on-demand ride.",
        ),
    )

    Tour = apps.get_model("content", "Tour")
    for tour in TOURS:
        Tour.objects.update_or_create(slug=tour["slug"], defaults=tour)


def unseed(apps, schema_editor):
    Tour = apps.get_model("content", "Tour")
    Tour.objects.filter(slug__in=[t["slug"] for t in TOURS]).delete()
    apps.get_model("content", "HomeContent").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
