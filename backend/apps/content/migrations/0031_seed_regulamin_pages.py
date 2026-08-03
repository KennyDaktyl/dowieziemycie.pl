# Regulamin for both brands — same clauses (pricing/VAT, deposit + Stripe
# payment, 24h cancellation window, statutory withdrawal-right exemption for
# transport services with a fixed date), only the trading name/branding line
# differs. Draft content — flagged to the user as needing a lawyer's review
# before being treated as final, especially the consumer-rights clauses.

from django.db import migrations

COMPANY_BLOCK_PL = (
    "**Usługodawca:** Michał Pielak, prowadzący działalność gospodarczą pod firmą "
    "MIKTEL Michał Pielak, NIP 6782805234, ul. Wspólna 2, 32-061 Rybna "
    "(dalej: „Usługodawca”)."
)
COMPANY_BLOCK_EN = (
    "**Service provider:** Michał Pielak, trading as MIKTEL Michał Pielak, "
    "NIP (Polish Tax ID) 6782805234, ul. Wspólna 2, 32-061 Rybna, Poland "
    "(hereinafter: the “Provider”)."
)


def _body_pl(brand: str) -> str:
    return f"""{COMPANY_BLOCK_PL}

## §1 Postanowienia ogólne

1. Niniejszy regulamin określa zasady świadczenia usług przewozu osób przez \
Usługodawcę za pośrednictwem serwisu {brand}, w tym zasady rezerwacji, płatności, \
anulowania oraz reklamacji.
2. Klientem może być każda osoba fizyczna, która dokonuje rezerwacji kursu za \
pośrednictwem serwisu {brand} (dalej: „Klient”).
3. Kontakt z Usługodawcą możliwy jest przez dane wskazane na stronie serwisu \
{brand} w zakładce Kontakt.

## §2 Przedmiot usługi

1. Usługodawca świadczy usługi przewozu osób na trasach i w terminach wskazanych \
przez Klienta podczas rezerwacji, pojazdami wskazanymi w ofercie.
2. Liczba pasażerów oraz ewentualny dodatkowy bagaż powinny zostać wskazane przez \
Klienta przy rezerwacji — Usługodawca ma prawo odmówić realizacji kursu lub \
zaproponować inny pojazd, jeśli rzeczywista liczba osób/bagażu przekracza zgłoszoną.

## §3 Rezerwacja

1. Rezerwacji dokonuje się poprzez formularz na stronie {brand}, podając adres \
odbioru, adres docelowy, termin kursu oraz numer telefonu.
2. Rezerwacja wymaga potwierdzenia przez Usługodawcę (dyspozytora), który ustala \
ostateczną cenę kursu oraz wysokość zaliczki. O potwierdzeniu Klient jest \
informowany SMS-em i/lub e-mailem.
3. Rezerwacja jest wiążąca po opłaceniu zaliczki w terminie wskazanym w \
potwierdzeniu — brak wpłaty w tym terminie powoduje automatyczne anulowanie \
rezerwacji i zwolnienie terminu.

## §4 Ceny i płatności

1. Wszystkie ceny podawane na stronie {brand} są cenami **brutto** (zawierają \
podatek VAT w stawce 23%). Na życzenie Klienta Usługodawca wskazuje kwotę netto \
oraz wysokość podatku VAT.
2. Warunkiem potwierdzenia rezerwacji jest wpłata zaliczki w wysokości ustalonej \
przez Usługodawcę (zwykle ok. 30% ceny kursu, każdorazowo wskazana w \
potwierdzeniu rezerwacji). Pozostała część należności płatna jest kierowcy w dniu \
realizacji kursu, chyba że strony ustalą inaczej.
3. Płatność zaliczki odbywa się online, za pośrednictwem operatora płatności \
Stripe — dostępne metody płatności to karta płatnicza oraz BLIK. Usługodawca nie \
przechowuje danych karty płatniczej Klienta — dane te przetwarzane są wyłącznie \
przez Stripe.

## §5 Anulowanie rezerwacji i zwrot zaliczki

1. Klient może bezpłatnie anulować rezerwację i otrzymać pełny zwrot wpłaconej \
zaliczki, jeśli anulowanie nastąpi **nie później niż 24 godziny przed planowaną \
godziną rozpoczęcia kursu**.
2. Anulowanie w terminie krótszym niż 24 godziny przed kursem, jak również \
niestawienie się Klienta w umówionym miejscu i czasie bez wcześniejszego \
anulowania, skutkuje utratą wpłaconej zaliczki.
3. Niezależnie od powyższego, Klientowi przysługuje **jednorazowe prawo do \
przełożenia terminu kursu** bez utraty zaliczki, o ile zgłosi taką potrzebę z \
odpowiednim wyprzedzeniem i nowy termin zostanie zaakceptowany przez Usługodawcę \
(w miarę dostępności kierowców).
4. Zwrot zaliczki następuje tym samym kanałem płatności, którym została dokonana \
wpłata, w terminie do 14 dni roboczych.

## §6 Prawo odstąpienia od umowy

Zgodnie z art. 38 pkt 12 ustawy z dnia 30 maja 2014 r. o prawach konsumenta, \
prawo odstąpienia od umowy zawartej na odległość **nie przysługuje** w \
odniesieniu do umów o świadczenie usług w zakresie przewozu osób, jeżeli w \
umowie oznaczono dzień lub okres świadczenia usługi — co ma miejsce w przypadku \
każdej rezerwacji dokonanej za pośrednictwem serwisu {brand}. Zasady anulowania \
rezerwacji reguluje wyłącznie §5 niniejszego regulaminu.

## §7 Reklamacje

1. Reklamacje dotyczące zrealizowanej usługi Klient może zgłaszać za \
pośrednictwem danych kontaktowych wskazanych na stronie {brand}, w terminie 14 \
dni od dnia realizacji kursu.
2. Usługodawca rozpatruje reklamację w terminie 14 dni od jej otrzymania.

## §8 Dane osobowe

Administratorem danych osobowych Klienta jest Usługodawca. Dane przetwarzane są \
w celu realizacji rezerwacji i płatności, w tym są przekazywane operatorowi \
płatności Stripe oraz operatorowi SMS w zakresie niezbędnym do realizacji usługi. \
Szczegółowe zasady przetwarzania danych osobowych zostaną określone w odrębnej \
polityce prywatności.

## §9 Postanowienia końcowe

1. W sprawach nieuregulowanych niniejszym regulaminem zastosowanie mają \
przepisy prawa polskiego, w tym Kodeksu cywilnego oraz ustawy o prawach \
konsumenta.
2. Usługodawca zastrzega sobie prawo do zmiany regulaminu — zmiany nie mają \
wpływu na rezerwacje potwierdzone przed dniem wejścia w życie zmian.
"""


def _body_en(brand: str) -> str:
    return f"""{COMPANY_BLOCK_EN}

## §1 General provisions

1. These terms set out the rules for providing passenger transport services by \
the Provider through the {brand} service, including booking, payment, \
cancellation and complaint procedures.
2. Any individual who books a ride through {brand} may be a Customer.
3. The Provider can be contacted via the details listed on the {brand} Contact \
page.

## §2 Scope of the service

1. The Provider carries passengers on the route and at the time specified by the \
Customer at booking, using the vehicle indicated in the offer.
2. The number of passengers and any extra luggage must be declared at booking — \
the Provider may refuse the ride or offer a different vehicle if the actual \
number of passengers/luggage exceeds what was declared.

## §3 Booking

1. Bookings are made via the form on the {brand} website, providing the pickup \
address, destination, ride time and phone number.
2. A booking requires confirmation by the Provider (dispatcher), who sets the \
final price and the deposit amount. The Customer is notified of the confirmation \
by SMS and/or email.
3. A booking becomes binding once the deposit is paid within the deadline stated \
in the confirmation — failure to pay in time automatically cancels the booking \
and releases the time slot.

## §4 Prices and payments

1. All prices shown on {brand} are **gross prices** (they include 23% VAT). On \
request, the Provider will state the net amount and the VAT amount separately.
2. Confirming a booking requires paying a deposit in the amount set by the \
Provider (typically around 30% of the ride price, always stated in the booking \
confirmation). The remaining balance is payable to the driver on the day of the \
ride, unless otherwise agreed.
3. The deposit is paid online via the payment processor Stripe — available \
methods are card payment and BLIK. The Provider does not store the Customer's \
card details — these are processed solely by Stripe.

## §5 Cancellation and deposit refunds

1. The Customer may cancel a booking free of charge and receive a full deposit \
refund if the cancellation is made **no later than 24 hours before the \
scheduled ride time**.
2. Cancelling less than 24 hours before the ride, or failing to show up at the \
agreed place and time without prior cancellation, forfeits the deposit.
3. Regardless of the above, the Customer has a **one-time right to reschedule** \
the ride without losing the deposit, provided this is requested with reasonable \
notice and the new time is accepted by the Provider (subject to driver \
availability).
4. Deposit refunds are made via the same payment method used for the original \
payment, within 14 business days.

## §6 Right of withdrawal

Under Polish consumer law (Art. 38(12) of the Act of 30 May 2014 on Consumer \
Rights), the statutory right of withdrawal from a distance contract **does not \
apply** to passenger transport services where the contract specifies a fixed \
day or period for performing the service — which is the case for every booking \
made through {brand}. Cancellation is governed solely by §5 of these terms.

## §7 Complaints

1. Complaints about a completed ride may be submitted via the contact details \
listed on {brand}, within 14 days of the ride.
2. The Provider will respond to a complaint within 14 days of receiving it.

## §8 Personal data

The Provider is the controller of the Customer's personal data. Data is \
processed to fulfil bookings and payments, and is shared with the payment \
processor Stripe and the SMS provider to the extent necessary to deliver the \
service. Detailed data-processing rules will be set out in a separate privacy \
policy.

## §9 Final provisions

1. Matters not covered by these terms are governed by Polish law, including the \
Civil Code and the Act on Consumer Rights.
2. The Provider reserves the right to amend these terms — changes do not affect \
bookings confirmed before the changes take effect.
"""


def forwards(apps, schema_editor):
    ContentPage = apps.get_model("content", "ContentPage")
    ContentPage.objects.update_or_create(
        slug="regulamin",
        defaults=dict(
            site="dowieziemycie",
            page_type="REGULAMIN",
            title_pl="Regulamin",
            title_en="Terms of Service",
            body_pl=_body_pl("dowieziemycie.pl"),
            body_en=_body_en("dowieziemycie.pl"),
            seo_title_pl="Regulamin | dowieziemycie.pl",
            seo_title_en="Terms of Service | dowieziemycie.pl",
            is_published=True,
        ),
    )
    ContentPage.objects.update_or_create(
        slug="regulamin-transfer247",
        defaults=dict(
            site="transfer247",
            page_type="REGULAMIN",
            title_pl="Regulamin",
            title_en="Terms of Service",
            body_pl=_body_pl("transfer247.pl"),
            body_en=_body_en("transfer247.pl"),
            seo_title_pl="Regulamin | transfer247.pl",
            seo_title_en="Terms of Service | transfer247.pl",
            is_published=True,
        ),
    )


def backwards(apps, schema_editor):
    apps.get_model("content", "ContentPage").objects.filter(
        slug__in=["regulamin", "regulamin-transfer247"],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0030_alter_contentpage_page_type"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
