# Same SEO audit finding as 0024, applied to the dowieziemycie.pl homepage
# (thin content flagged by an on-page checker) — seeds the about_pl/about_en
# paragraph added by that migration for the "dowieziemycie" site row.

from django.db import migrations


ABOUT_DOWIEZIEMYCIE_PL = (
    "dowieziemycie.pl to lokalny transport spod Krakowa, prowadzony przez "
    "jednego, sprawdzonego kierowcę — nie sieć anonimowych taksówek. "
    "Obsługujemy stałe kierunki: Rybną, Liszki, Kaszów, Czernichów, Sankę, "
    "Alwernię i Przeginię Narodową, o każdej porze dnia i nocy, także w "
    "niedziele. Cenę znasz z góry — zależy od realnej odległości trasy, a "
    "rezerwacja z wyprzedzeniem oznacza niższą stawkę niż zamówienie na "
    "już. Po opłaceniu zaliczki przez BLIK widzisz na mapie dokładną "
    "pozycję kierowcy i szacowany czas dojazdu na żywo, więc wiesz, kiedy "
    "dokładnie podjedzie pod Twoje drzwi. Nie trzeba czekać w niepewności "
    "ani negocjować ceny na miejscu. Rezerwację złożysz online w kilka "
    "minut — jako stały klient czy gość odwiedzający okolice Krakowa, w "
    "dzień powszedni czy w środku nocy."
)

ABOUT_DOWIEZIEMYCIE_EN = (
    "dowieziemycie.pl is local transport around Kraków, run by one "
    "trusted driver — not an anonymous taxi network. We cover fixed "
    "directions: Rybna, Liszki, Kaszów, Czernichów, Sanka, Alwernia and "
    "Przeginia Narodowa, any time of day or night, including Sundays. You "
    "know the price upfront — based on the real route distance — and "
    "booking ahead means a lower fare than an on-demand ride. After "
    "paying the BLIK deposit, you can track the driver's exact position "
    "and live ETA on the map, so you know exactly when the car reaches "
    "your door. No waiting in uncertainty, no haggling on the spot. Book "
    "online in minutes — whether you're a regular or just visiting the "
    "area around Kraków, on a weekday or in the middle of the night."
)


def forwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="dowieziemycie").update(
        about_pl=ABOUT_DOWIEZIEMYCIE_PL,
        about_en=ABOUT_DOWIEZIEMYCIE_EN,
    )


def backwards(apps, schema_editor):
    HomeContent = apps.get_model("content", "HomeContent")
    HomeContent.objects.filter(site="dowieziemycie").update(
        about_pl="", about_en="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0024_homecontent_about"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
