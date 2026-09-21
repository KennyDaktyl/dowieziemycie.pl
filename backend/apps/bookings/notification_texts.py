"""Customer-facing SMS / e-mail copy in every language the sites offer (pl, en,
de). The language is the one the customer was browsing in when they booked
(Booking.language) or requested a login code — see config.sites.

Only messages addressed to the *customer* live here. Dispatcher and driver
notifications are internal and stay Polish in notifications.py.

The SMSAPI gateway garbles non-ASCII (see apps.accounts.sms), which strips
diacritics at send time. The German SMS copy is therefore spelled with
ae/oe/ue/ss up front ("Gueltig", not "Gültig" -> "Gultig"); English is ASCII
anyway. E-mail copy uses proper characters.

Placeholders: {site} brand name, {when} "dd.mm HH:MM"; amounts arrive
pre-formatted (see notifications._money).
"""

from apps.accounts.sms import sms_safe
from config.sites import DEFAULT_LANGUAGE

TEXTS = {
    "pl": {
        "otp_sms": "{site} - Twoj kod: {code}. Wazny {minutes} min.",
        "tagline_dowieziemycie": "Twój sąsiad z busem",
        "tagline_transfer247": "Transfery lotniskowe bez stresu",
        # --- confirmation -------------------------------------------------
        "confirmed_sms": (
            "{site}: Rezerwacja na {when} potwierdzona! Aby kurs był ważny, zapłać zaliczkę {deposit} "
            "w ciągu {minutes} min (cena kursu: {price}): {link}"
        ),
        "confirmed_sms_nolink": (
            "{site}: Rezerwacja na {when} potwierdzona! Aby kurs byl wazny, zaplac zaliczke {deposit} "
            "w ciagu {minutes} min - zaloguj sie na stronie {site} i zaplac w panelu klienta (cena kursu: {price})."
        ),
        "confirmed_subject": "{site}: rezerwacja potwierdzona — zapłać zaliczkę",
        "confirmed_heading": "Rezerwacja potwierdzona!",
        "confirmed_line1": "Twoja rezerwacja na {when} została potwierdzona.",
        "confirmed_line2": "Cena: {price}, zaliczka: {deposit}.",
        "confirmed_line3": (
            "Aby kurs był ważny, zapłać zaliczkę w ciągu {minutes} minut — w przeciwnym razie rezerwacja "
            "wygaśnie. Możesz to zrobić przyciskiem poniżej albo linkiem z SMS-a."
        ),
        "confirmed_cta": "Zapłać zaliczkę",
        # --- price change -------------------------------------------------
        "price_changed_sms": "{site}: Cena Twojego kursu została zaktualizowana - nowa cena: {price}.",
        "price_changed_remaining": " Do dopłaty: {remaining}.",
        # --- driver en route ----------------------------------------------
        "en_route_sms": (
            "{site}: Kierowca {driver} jedzie do Ciebie! Kurs: {pickup}. "
            "Kod do sledzenia: {code}, aktywny od {active_from}."
        ),
        # --- ride lifecycle -----------------------------------------------
        "ride_started_sms": "{site}: Kurs się rozpoczął. Miłej podróży!",
        "ride_finished_sms": "{site}: Kurs zakończony. Dziękujemy za skorzystanie z naszych usług!",
        "ride_finished_subject": "{site}: kurs zakończony — dziękujemy",
        "ride_finished_heading": "Dziękujemy za skorzystanie z naszych usług!",
        "ride_finished_line": "Kurs został zakończony. Mamy nadzieję, że podróż minęła komfortowo.",
        "ride_finished_cta": "Zarezerwuj kolejny kurs",
        # --- reschedule ---------------------------------------------------
        "rescheduled_sms": "{site}: Termin Twojego kursu ({pickup} -> {dropoff}) zostal zmieniony z {old} na {new}.",
        "rescheduled_email_line": (
            "{site}: Termin Twojego kursu ({pickup} → {dropoff}) został zmieniony z {old} na {new}."
        ),
        "rescheduled_subject": "{site}: zmiana terminu kursu",
        "rescheduled_heading": "Zmiana terminu kursu",
        "rescheduled_cta": "Zobacz szczegóły w panelu",
        # --- cancellation by dispatcher -----------------------------------
        "cancelled_sms": "{site}: Twoj kurs na {when} ({pickup} -> {dropoff}) zostal anulowany. Przepraszamy za utrudnienia.",
        "cancelled_email_line": (
            "{site}: Twój kurs na {when} ({pickup} → {dropoff}) został anulowany. Przepraszamy za utrudnienia."
        ),
        "cancelled_subject": "{site}: kurs anulowany",
        "cancelled_heading": "Kurs anulowany",
        "cancelled_cta": "Zarezerwuj nowy termin",
        "currency_fallback": "zł",
        "deposit_link_sms": (
            "{site}: Przypomnienie - aby kurs na {when} był ważny, zapłać zaliczkę {deposit} do {deadline}: {link}"
        ),
        "remainder_link_sms": "{site}: Prosimy o zapłatę pozostałej kwoty {amount} za kurs na {when}: {link}",
        "payment_received_deposit_sms": (
            "{site}: Dziękujemy, otrzymaliśmy zaliczkę {amount}. Twój kurs na {when} jest potwierdzony!"
        ),
        "payment_received_remainder_sms": "{site}: Dziękujemy, otrzymaliśmy wpłatę {amount}. Kurs jest opłacony w całości.",
        "checkout_product_deposit": "Zaliczka za przejazd",
        "checkout_product_remainder": "Dopłata za przejazd",
    },
    "en": {
        "otp_sms": "{site} - Your code: {code}. Valid for {minutes} min.",
        "tagline_dowieziemycie": "Your neighbourhood van",
        "tagline_transfer247": "Stress-free airport transfers",
        "confirmed_sms": (
            "{site}: Your booking for {when} is confirmed! To keep it valid, pay the {deposit} deposit "
            "within {minutes} min (ride price: {price}): {link}"
        ),
        "confirmed_sms_nolink": (
            "{site}: Your booking for {when} is confirmed! To keep it valid, pay the {deposit} deposit within "
            "{minutes} min - log in on the {site} website and pay in your account (ride price: {price})."
        ),
        "confirmed_subject": "{site}: booking confirmed — pay the deposit",
        "confirmed_heading": "Booking confirmed!",
        "confirmed_line1": "Your booking for {when} has been confirmed.",
        "confirmed_line2": "Price: {price}, deposit: {deposit}.",
        "confirmed_line3": (
            "To keep your booking valid, please pay the deposit within {minutes} minutes — otherwise it "
            "will expire. Use the button below or the link from the text message."
        ),
        "confirmed_cta": "Pay the deposit",
        "price_changed_sms": "{site}: The price of your ride has been updated - new price: {price}.",
        "price_changed_remaining": " Remaining to pay: {remaining}.",
        "en_route_sms": (
            "{site}: Your driver {driver} is on the way! Ride: {pickup}. "
            "Tracking code: {code}, active from {active_from}."
        ),
        "ride_started_sms": "{site}: Your ride has started. Have a pleasant trip!",
        "ride_finished_sms": "{site}: Your ride is complete. Thank you for choosing us!",
        "ride_finished_subject": "{site}: ride completed — thank you",
        "ride_finished_heading": "Thank you for riding with us!",
        "ride_finished_line": "Your ride is complete. We hope you had a comfortable journey.",
        "ride_finished_cta": "Book another ride",
        "rescheduled_sms": "{site}: The time of your ride ({pickup} -> {dropoff}) has been changed from {old} to {new}.",
        "rescheduled_email_line": (
            "{site}: The time of your ride ({pickup} → {dropoff}) has been changed from {old} to {new}."
        ),
        "rescheduled_subject": "{site}: ride time changed",
        "rescheduled_heading": "Ride time changed",
        "rescheduled_cta": "View details in your account",
        "cancelled_sms": "{site}: Your ride on {when} ({pickup} -> {dropoff}) has been cancelled. We apologise for the inconvenience.",
        "cancelled_email_line": (
            "{site}: Your ride on {when} ({pickup} → {dropoff}) has been cancelled. "
            "We apologise for the inconvenience."
        ),
        "cancelled_subject": "{site}: ride cancelled",
        "cancelled_heading": "Ride cancelled",
        "cancelled_cta": "Book a new time",
        "currency_fallback": "PLN",
        "deposit_link_sms": (
            "{site}: Reminder - to keep your ride on {when} valid, pay the {deposit} deposit by {deadline}: {link}"
        ),
        "remainder_link_sms": "{site}: Please pay the remaining {amount} for your ride on {when}: {link}",
        "payment_received_deposit_sms": (
            "{site}: Thank you, we received your {amount} deposit. Your ride on {when} is confirmed!"
        ),
        "payment_received_remainder_sms": "{site}: Thank you, we received your {amount} payment. Your ride is paid in full.",
        "checkout_product_deposit": "Deposit for your ride",
        "checkout_product_remainder": "Remaining payment for your ride",
    },
    "de": {
        "otp_sms": "{site} - Ihr Code: {code}. Gueltig {minutes} Min.",
        "tagline_dowieziemycie": "Ihr Nachbar mit dem Bus",
        "tagline_transfer247": "Stressfreie Flughafentransfers",
        "confirmed_sms": (
            "{site}: Ihre Buchung fuer {when} wurde bestaetigt! Damit sie gueltig bleibt, zahlen Sie die "
            "Anzahlung von {deposit} innerhalb von {minutes} Min. (Fahrpreis: {price}): {link}"
        ),
        "confirmed_sms_nolink": (
            "{site}: Ihre Buchung fuer {when} wurde bestaetigt! Damit sie gueltig bleibt, zahlen Sie die "
            "Anzahlung von {deposit} innerhalb von {minutes} Min. - melden Sie sich auf der Website {site} an "
            "und zahlen Sie im Kundenbereich (Fahrpreis: {price})."
        ),
        "confirmed_subject": "{site}: Buchung bestätigt — bitte Anzahlung leisten",
        "confirmed_heading": "Buchung bestätigt!",
        "confirmed_line1": "Ihre Buchung für {when} wurde bestätigt.",
        "confirmed_line2": "Preis: {price}, Anzahlung: {deposit}.",
        "confirmed_line3": (
            "Damit Ihre Buchung gültig bleibt, zahlen Sie die Anzahlung bitte innerhalb von {minutes} Minuten — "
            "sonst verfällt sie. Nutzen Sie dazu die Schaltfläche unten oder den Link aus der SMS."
        ),
        "confirmed_cta": "Anzahlung leisten",
        "price_changed_sms": "{site}: Der Preis Ihrer Fahrt wurde aktualisiert - neuer Preis: {price}.",
        "price_changed_remaining": " Noch zu zahlen: {remaining}.",
        "en_route_sms": (
            "{site}: Ihr Fahrer {driver} ist auf dem Weg zu Ihnen! Fahrt: {pickup}. "
            "Tracking-Code: {code}, aktiv ab {active_from}."
        ),
        "ride_started_sms": "{site}: Ihre Fahrt hat begonnen. Gute Reise!",
        "ride_finished_sms": "{site}: Ihre Fahrt ist beendet. Vielen Dank, dass Sie uns gewaehlt haben!",
        "ride_finished_subject": "{site}: Fahrt beendet — vielen Dank",
        "ride_finished_heading": "Vielen Dank, dass Sie mit uns gefahren sind!",
        "ride_finished_line": "Ihre Fahrt ist beendet. Wir hoffen, Sie hatten eine angenehme Reise.",
        "ride_finished_cta": "Weitere Fahrt buchen",
        "rescheduled_sms": "{site}: Der Termin Ihrer Fahrt ({pickup} -> {dropoff}) wurde von {old} auf {new} geaendert.",
        "rescheduled_email_line": (
            "{site}: Der Termin Ihrer Fahrt ({pickup} → {dropoff}) wurde von {old} auf {new} geändert."
        ),
        "rescheduled_subject": "{site}: Fahrttermin geändert",
        "rescheduled_heading": "Fahrttermin geändert",
        "rescheduled_cta": "Details im Kundenbereich ansehen",
        "cancelled_sms": "{site}: Ihre Fahrt am {when} ({pickup} -> {dropoff}) wurde storniert. Wir bitten um Entschuldigung.",
        "cancelled_email_line": (
            "{site}: Ihre Fahrt am {when} ({pickup} → {dropoff}) wurde storniert. Wir bitten um Entschuldigung."
        ),
        "cancelled_subject": "{site}: Fahrt storniert",
        "cancelled_heading": "Fahrt storniert",
        "cancelled_cta": "Neuen Termin buchen",
        "currency_fallback": "PLN",
        "deposit_link_sms": (
            "{site}: Erinnerung - damit Ihre Fahrt am {when} gueltig bleibt, zahlen Sie die Anzahlung "
            "von {deposit} bis {deadline}: {link}"
        ),
        "remainder_link_sms": "{site}: Bitte zahlen Sie den Restbetrag von {amount} fuer Ihre Fahrt am {when}: {link}",
        "payment_received_deposit_sms": (
            "{site}: Vielen Dank, Ihre Anzahlung von {amount} ist eingegangen. Ihre Fahrt am {when} ist bestaetigt!"
        ),
        "payment_received_remainder_sms": (
            "{site}: Vielen Dank, Ihre Zahlung von {amount} ist eingegangen. Die Fahrt ist vollstaendig bezahlt."
        ),
        "checkout_product_deposit": "Anzahlung für Ihre Fahrt",
        "checkout_product_remainder": "Restzahlung für Ihre Fahrt",
    },
}


def _is_sms(key: str) -> bool:
    return "sms" in key or key == "price_changed_remaining"  # the latter is appended to an SMS


def text(language: str, key: str, **values) -> str:
    """One customer-facing string in `language` (Polish if unknown). SMS
    strings come back as plain ASCII (see apps.accounts.sms.sms_safe) — what
    is stored and logged is exactly what the handset receives, including any
    diacritics in a customer-typed address or a driver's name."""
    catalog = TEXTS.get(language) or TEXTS[DEFAULT_LANGUAGE]
    result = catalog[key].format(**values)
    return sms_safe(result) if _is_sms(key) else result
