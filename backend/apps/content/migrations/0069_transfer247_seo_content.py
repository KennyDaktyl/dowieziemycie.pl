# transfer247.pl SEO content pass (2026-10).
#
# - SEO titles <= 60 chars, descriptions 140-155, for every route and tour and
#   for the blog posts that were over/under. Prices appear only as tokens —
#   `{price}` (this item) or `{price:route|tour:<slug>}` — which the frontend
#   fills with the live price; hard-coded amounts had drifted by up to 300 zl
#   (blog: Balice-Zakopane "od 399 zl" vs 599 zl, Auschwitz 449 vs 699, ...).
#   Requires the transfer247 frontend with fillPriceTokens deployed FIRST.
# - Removes internal SEO notes that had been published as page copy
#   ("Dla SEO najwazniejsze frazy to...", "This page targets searches...").
# - Adds contextual internal links (>= 2 per post), the "transfer z Pyrzowic do
#   Krakowa" anchor + CTA, and a short "Transfer na lotnisko Balice z Krakowa i
#   okolic" section on balice-krakow that points at the dedicated drop-off page.
# - Full PL text for closest-airport-to-auschwitz (was a 2-sentence stub).
# - Fixes the broken EN H1 of transfer-na-lotnisko-balice ("from 35€34").
#
# Every body edit is an exact-substring replacement applied only when the
# original text is still there, so an Admin edit made in the meantime is
# never clobbered (the migration just skips that edit). Not reversible in
# content terms — backwards is a no-op.

import re

from django.db import migrations

# --- SEO title/description per object and locale -------------------------
# {price} = this route's/tour's live "from" price (filled by the frontend);
# {price:route:<slug>} / {price:tour:<slug>} = another item's price.

ROUTE_SEO = {
    "balice-krakow": {
        "pl": ("Transfer z lotniska Balice do Krakowa od {price} | 24/7",
               "Transfer z lotniska Kraków Balice do hotelu lub centrum Krakowa. Stała cena od {price}, odbiór z tablicą, śledzenie lotu, bus do 6 osób, 24/7."),
        "en": ("Krakow Airport Transfer to City & Hotel from {price}",
               "Private Krakow Balice airport transfer to your hotel or the city centre. Fixed price from {price}, meet & greet, flight tracking, van for up to 6, 24/7."),
        "de": ("Flughafentransfer Krakau Balice ab {price} | 24/7",
               "Privater Transfer vom Flughafen Krakau-Balice zum Hotel oder ins Zentrum. Festpreis ab {price}, Namensschild, Flugverfolgung, Van bis 6 Personen."),
    },
    "katowice-krakow": {
        "pl": ("Transfer Pyrzowice – Kraków od {price} | Lotnisko Katowice",
               "Transfer z lotniska Katowice-Pyrzowice do Krakowa i na lotnisko. Ok. 1h30, stała cena od {price}, odbiór z terminala, śledzenie lotu 24/7, do 6 osób."),
        "en": ("Katowice Airport to Krakow Transfer from {price} | 24/7",
               "Private transfer from Katowice Pyrzowice airport to Krakow and back. About 1h30, fixed price from {price}, terminal pickup, flight tracking 24/7."),
        "de": ("Transfer Flughafen Kattowitz – Krakau ab {price} | 24/7",
               "Privater Transfer vom Flughafen Kattowitz-Pyrzowice nach Krakau und zurück. Ca. 1,5 h, Festpreis ab {price}, Abholung am Terminal, bis 6 Personen."),
    },
    "balice-zakopane": {
        "pl": ("Transfer Balice – Zakopane od {price} | Lotnisko Kraków",
               "Prywatny transfer z lotniska Kraków Balice do Zakopanego pod hotel. Ok. 2 h, stała cena od {price}, bus do 6 osób, śledzenie lotu, 24/7. Zarezerwuj."),
        "en": ("Krakow Airport to Zakopane Transfer from {price} | 24/7",
               "Private transfer from Krakow Balice airport to your Zakopane hotel. About 2 h, fixed price from {price}, van for up to 6, flight tracking, 24/7."),
        "de": ("Transfer Flughafen Krakau – Zakopane ab {price} | 24/7",
               "Privater Transfer vom Flughafen Krakau-Balice zu Ihrem Hotel in Zakopane. Ca. 2 h, Festpreis ab {price}, Van bis 6 Personen, Flugverfolgung, 24/7."),
    },
    "balice-katowice": {
        "pl": ("Transfer Balice – Pyrzowice (Kraków ↔ Katowice) | 24/7",
               "Transfer między lotniskami Kraków Balice i Katowice Pyrzowice w obie strony. Ok. 1h20, stała cena od {price}, bus do 6 osób, śledzenie lotu 24/7."),
        "en": ("Krakow – Katowice Airport Transfer from {price} | 24/7",
               "Transfer between Krakow Balice and Katowice Pyrzowice airports, both ways. About 1h20, fixed price from {price}, van for up to 6, flight tracking 24/7."),
        "de": ("Transfer Flughafen Krakau – Kattowitz ab {price} | 24/7",
               "Transfer zwischen den Flughäfen Krakau-Balice und Kattowitz-Pyrzowice in beide Richtungen. Ca. 1,3 h, Festpreis ab {price}, Van bis 6 Personen."),
    },
    "krakow-energylandia": {
        "pl": ("Transfer Kraków – Energylandia w jedną stronę od {price}",
               "Przejazd w jedną stronę z Krakowa (hotel, dworzec PKP) do Energylandii w Zatorze. Ok. 1 h, stała cena od {price}, bus do 6 osób, 24/7. Zarezerwuj."),
        "en": ("One-Way Transfer Krakow – Energylandia from {price}",
               "One-way ride from Krakow (hotel or train station) to Energylandia in Zator. About 1 h, fixed price from {price}, van for up to 6 people, 24/7. Book."),
        "de": ("Einwegtransfer Krakau – Energylandia ab {price}",
               "Fahrt in eine Richtung von Krakau (Hotel, Bahnhof) zum Energylandia in Zator. Ca. 1 h, Festpreis ab {price}, Van bis 6 Personen, 24/7. Online buchen."),
    },
    "transfer-na-lotnisko-balice": {
        "pl": ("Transfer na lotnisko Balice z Krakowa od {price} | 24/7",
               "Transfer na lotnisko Kraków Balice spod domu lub hotelu w Krakowie. Stała cena od {price}, bus do 6 osób, dojazd z zapasem przed wylotem, 24/7."),
        "en": ("Transfer to Krakow Airport from {price} | 24/7",
               "Transfer to Krakow Balice airport from your home or hotel in Krakow. Fixed price from {price}, van for up to 6, on time for your flight, 24/7. Book online."),
        "de": ("Transfer zum Flughafen Krakau ab {price} | 24/7",
               "Transfer zum Flughafen Krakau-Balice von Ihrem Hotel oder Ihrer Adresse in Krakau. Festpreis ab {price}, Van bis 6 Personen, pünktlich, 24/7. Buchen."),
    },
    "dworzec-balice": {
        "pl": ("Transfer Dworzec Kraków – Lotnisko Balice od {price}",
               "Transfer z Dworca Głównego w Krakowie na lotnisko Balice i z powrotem. Ok. 25 min, stała cena od {price}, bus do 6 osób, 24/7. Zarezerwuj online."),
        "en": ("Krakow Train Station – Airport Transfer from {price}",
               "Transfer from Krakow Main Station to Balice airport and back. About 25 min, fixed price from {price}, van for up to 6 people, 24/7. Book your ride online."),
        "de": ("Transfer Bahnhof Krakau – Flughafen ab {price} | 24/7",
               "Transfer vom Hauptbahnhof Krakau zum Flughafen Balice und zurück. Ca. 25 Min., Festpreis ab {price}, Van bis 6 Personen, 24/7. Jetzt online buchen."),
    },
    "krakow-zakopane": {
        "pl": ("Transfer Kraków – Zakopane od {price} | Bus do 6 osób",
               "Prywatny transfer z Krakowa do Zakopanego spod hotelu pod nocleg. Ok. 2 h, stała cena od {price}, Multivan do 6 osób, 24/7. Zarezerwuj online."),
        "en": ("Krakow to Zakopane Private Transfer from {price} | 24/7",
               "Private transfer from your Krakow hotel to your Zakopane stay. About 2 h, fixed price from {price}, Multivan for up to 6 people, 24/7. Book online now."),
        "de": ("Privattransfer Krakau – Zakopane ab {price} | 24/7",
               "Privater Transfer von Ihrem Hotel in Krakau zur Unterkunft in Zakopane. Ca. 2 h, Festpreis ab {price}, Multivan bis 6 Personen, 24/7. Online buchen."),
    },
}

TOUR_SEO = {
    "krakow-energylandia": {
        "pl": ("Bus Kraków – Energylandia dla grupy do 6 osób | Transfer247",
               "Całodniowy wyjazd z Krakowa do Energylandii z powrotem: kierowca czeka cały dzień, bus do 6 osób, stała cena od {price} za grupę. Zarezerwuj online."),
        "en": ("Krakow – Energylandia Day Trip for up to 6 | Transfer247",
               "Full-day trip from Krakow to Energylandia and back: the driver waits all day, van for up to 6 people, fixed price from {price} per group. Book online."),
        "de": ("Tagesausflug Krakau – Energylandia bis 6 Personen",
               "Ganztägiger Ausflug von Krakau zum Energylandia mit Rückfahrt: Fahrer wartet den ganzen Tag, Van bis 6 Personen, Festpreis ab {price} pro Gruppe."),
    },
    "auschwitz-birkenau-transfer247": {
        "pl": ("Wycieczka do Auschwitz z Krakowa od {price} | Prywatny bus",
               "Prywatny transfer z Krakowa do Muzeum Auschwitz-Birkenau z powrotem. Kierowca czeka na miejscu, bus do 6 osób, stała cena od {price}, 24/7. Zarezerwuj."),
        "en": ("Auschwitz Tour from Krakow from {price} | Private Van",
               "Private trip from Krakow to the Auschwitz-Birkenau Memorial and back. Driver waits on site, van for up to 6 people, fixed price from {price}. Book online."),
        "de": ("Auschwitz-Ausflug ab Krakau ab {price} | Privat-Van",
               "Privater Ausflug von Krakau zur Gedenkstätte Auschwitz-Birkenau mit Rückfahrt. Fahrer wartet vor Ort, Van bis 6 Personen, Festpreis ab {price}."),
    },
    "wieliczka-transfer247": {
        "pl": ("Wycieczka do Wieliczki z Krakowa od {price} | Prywatny bus",
               "Prywatny transfer z Krakowa do Kopalni Soli Wieliczka z powrotem. Kierowca czeka na miejscu, bus do 6 osób, stała cena od {price}, 24/7. Zarezerwuj."),
        "en": ("Wieliczka Salt Mine Tour from Krakow from {price}",
               "Private trip from Krakow to the Wieliczka Salt Mine and back. Driver waits on site, van for up to 6 people, fixed price from {price}, 24/7. Book online now."),
        "de": ("Salzbergwerk Wieliczka ab Krakau ab {price} | Privat",
               "Privater Ausflug von Krakau zum Salzbergwerk Wieliczka mit Rückfahrt. Fahrer wartet vor Ort, Van bis 6 Personen, Festpreis ab {price}, 24/7. Buchen."),
    },
    "krakow-splyw-dunajcem": {
        "pl": ("Spływ Dunajcem z Krakowa od {price} | Prywatny bus 24/7",
               "Całodniowa wycieczka z Krakowa na spływ Dunajcem w Pieninach z powrotem. Kierowca czeka, bus do 6 osób, stała cena od {price} za grupę. Zarezerwuj."),
        "en": ("Dunajec Rafting Day Trip from Krakow from {price}",
               "Full-day trip from Krakow to Dunajec river rafting in the Pieniny and back. Driver waits, van for up to 6 people, fixed price from {price}. Book online."),
        "de": ("Dunajec-Floßfahrt ab Krakau ab {price} | Privat-Van",
               "Tagesausflug von Krakau zur Dunajec-Floßfahrt in den Pieninen mit Rückfahrt. Fahrer wartet, Van bis 6 Personen, Festpreis ab {price}. Online buchen."),
    },
}

# Blog: only the locales/fields that need fixing (None = leave as is).
BLOG_SEO = {
    "closest-airport-to-auschwitz": {
        "pl": (None,
               "Najbliższe lotnisko do Auschwitz: Kraków-Balice czy Katowice-Pyrzowice? Porównanie czasu dojazdu, kosztów i prywatnego transferu z lotniska do Muzeum."),
        "en": ("Closest Airport to Auschwitz: Krakow or Katowice? (2026)",
               "Which airport is closest to Auschwitz? Krakow vs Katowice compared: drive time, cost and a private transfer from the airport to the Memorial."),
        "de": ("Flughafen nahe Auschwitz: Krakau oder Kattowitz? (2026)",
               "Welcher Flughafen liegt am nächsten an Auschwitz? Krakau oder Kattowitz im Vergleich: Fahrzeit, Kosten und privater Transfer ab dem Flughafen."),
    },
    "katowice-pyrzowice-jak-dojechac-do-krakowa": {
        "pl": ("Pyrzowice – Kraków: bus, pociąg czy transfer? Ceny 2026",
               "Jak dojechać z lotniska Katowice-Pyrzowice do Krakowa? Bus, pociąg czy prywatny transfer od {price:route:katowice-krakow} – porównanie czasu przejazdu, wygody i cen w 2026 roku."),
        "en": (None,
               "How to get from Katowice Pyrzowice Airport to Krakow: bus, train or private transfer from {price:route:katowice-krakow}. Travel times, airport pickup and online booking."),
    },
    "katowice-pyrzowice-airport-to-krakow-transfer": {
        "pl": ("Transfer Katowice Pyrzowice – Kraków | Lotnisko KTW 24/7",
               "Prywatny transfer z lotniska Katowice-Pyrzowice do hotelu w Krakowie. Ok. 1,5 h, stała cena od {price:route:katowice-krakow}, bus do 6 osób, 24/7. Zarezerwuj online."),
        "en": (None,
               "Private transfer from Katowice Pyrzowice Airport to your Krakow hotel. About 1.5 h, fixed price from {price:route:katowice-krakow}, up to 6 people, 24/7. Book online."),
    },
    "transfer-z-lotniska-krakow-balice-kompletny-przewodnik-2026": {
        "pl": ("Transfer z lotniska Kraków Balice – przewodnik 2026", None),
        "de": ("Flughafentransfer Krakau Balice – Leitfaden 2026",
               "Flughafentransfer Krakau-Balice planen? So vermeiden Sie Stress und versteckte Gebühren: Festpreis, Gruppentransport und Flugüberwachung erklärt."),
    },
    "ile-kosztuje-transfer-na-lotnisko-balice": {
        "pl": (None,
               "Taxi, bus, własny samochód czy prywatny transfer? Porównujemy realne koszty dojazdu na lotnisko Kraków-Balice i podpowiadamy, kiedy transfer się opłaca."),
    },
    "balice-zakopane-ile-kosztuje": {
        "pl": (None,
               "Transfer z lotniska Kraków-Balice do Zakopanego: stała cena od {price:route:balice-zakopane}, 24/7, bez dopłat. Czas przejazdu, trasa, bagaż narciarski i rezerwacja online."),
    },
    "auschwitz-birkenau-jak-zaplanowac-wycieczke": {
        "pl": (None,
               "Jak zaplanować wycieczkę do Auschwitz-Birkenau z Krakowa: bilety, zasady zwiedzania i prywatny transfer z kierowcą czekającym na miejscu od {price:tour:auschwitz-birkenau-transfer247}."),
    },
    "kopalnia-soli-wieliczka-transfer-i-bilety": {
        "pl": (None,
               "Transfer z Krakowa do Kopalni Soli Wieliczka od {price:tour:wieliczka-transfer247}, kierowca czeka na miejscu. Ceny biletów, trasy zwiedzania i ile czasu zaplanować na wyjazd."),
    },
}

# --- Body edits: (kind, slug, field, old, new) -----------------------------
# Exact-substring replacements; `old` must exist verbatim. kind: route|tour|blog.

AUSCHWITZ_TABLE_OLD = (
    "| Toyota Auris Hybrid | do 3 osób | **449 zł** |\n"
    "| Ford Tourneo Custom | do 8 osób | **549 zł** |"
)
WIELICZKA_TABLE_OLD = (
    "| Toyota Auris Hybrid | do 3 osób | **259 zł** |\n"
    "| Ford Tourneo Custom | do 8 osób | **319 zł** |"
)

REPLACE = [
    # Leaked internal SEO notes -> customer-facing copy.
    ("route", "balice-krakow", "body_pl",
     "Ta trasa odpowiada na zapytania **transfery lotniskowe Kraków**, **transfer z lotniska Balice do hotelu** oraz **Balice to Krakow**. ",
     "Kierowca czeka na Ciebie w hali przylotów z tablicą z Twoim nazwiskiem — o każdej porze, także w nocy. "),
    ("route", "balice-krakow", "body_en",
     "This route answers searches for Krakow airport transfers, transfer from Balice airport to hotel, and Balice to Krakow. ",
     "Your driver waits in the arrivals hall with a name sign — at any hour, night arrivals included. "),
    ("route", "balice-krakow", "body_de",
     "Diese Strecke beantwortet Suchanfragen wie Flughafentransfer Krakau, Transfer vom Flughafen Balice zum Hotel und Balice to Krakow. ",
     "Ihr Fahrer wartet in der Ankunftshalle mit einem Namensschild — zu jeder Uhrzeit, auch nachts. "),
    ("route", "katowice-krakow", "body_pl",
     " To strona dla osób szukających fraz **pyrzowice kraków**, **bus pyrzowice kraków**, **transfer kraków pyrzowice** oraz **katowice airport to krakow**.",
     " Kierowca odbiera Cię z terminala, śledzi Twój lot i jedzie prosto pod wskazany adres w Krakowie."),
    ("route", "katowice-krakow", "body_en",
     " This page targets searches such as **Katowice Airport to Krakow**, **Pyrzowice to Krakow transfer**, **KTW airport to Krakow hotel** and **bus Pyrzowice Krakow**.",
     " The driver tracks your flight and waits for you at arrivals, even if you land late."),
    ("route", "dworzec-balice", "body_en",
     " This page answers searches such as **Krakow train station to airport**, **Krakow airport transfer from station** and **how to get from Krakow Glowny to Balice Airport**.",
     " The driver picks you up at the station and takes you straight to the departures terminal — no luggage on trains or buses."),
    # Tour vs one-way transfer to Energylandia: say which one this is.
    ("tour", "krakow-energylandia", "body_pl",
     "Wycieczka lub transport z Krakowa do Energylandii w Zatorze, z odbiorem",
     "Całodniowa wycieczka z Krakowa do Energylandii w Zatorze i z powrotem, z odbiorem"),
    ("tour", "krakow-energylandia", "body_pl",
     " Strona odpowiada na zapytania **transport Kraków Energylandia**, **bus z Krakowa do Energylandii**, **ile jest z Krakowa do Energylandii** i **Kraków to Energylandia**.",
     " Kierowca czeka na Was cały dzień i odwozi z powrotem do Krakowa, gdy skończycie zabawę. Potrzebujesz tylko dojazdu w jedną stronę? Wybierz [transfer Kraków – Energylandia](/transfery/krakow-energylandia)."),
    ("tour", "krakow-energylandia", "body_en",
     "Private Krakow to Energylandia transfer or day trip with pickup",
     "Private full-day trip from Krakow to Energylandia and back, with pickup"),
    ("tour", "krakow-energylandia", "body_en",
     " This page targets searches such as **how to get to Energylandia from Krakow**, **Krakow to Energylandia transfer** and **Energylandia from Krakow**.",
     " The driver waits for you all day and takes you back to Krakow when you're done. Only need a one-way ride? Book the [Krakow – Energylandia transfer](/transfery/krakow-energylandia)."),
    # transfer-na-lotnisko-balice: broken EN H1 ("from 35€34") and hard-coded prices.
    ("route", "transfer-na-lotnisko-balice", "h1_en",
     "Transfer to Kraków-Balice Airport — from 35€34",
     "Transfer to Kraków-Balice Airport from Kraków"),
    ("route", "transfer-na-lotnisko-balice", "body_pl",
     "## Dlaczego 149 zł, a nie więcej?",
     "## Dlaczego taniej niż odbiór z lotniska?"),
    ("route", "transfer-na-lotnisko-balice", "body_pl",
     "Nie, 149 zł to stała cena",
     "Nie, {price:route:transfer-na-lotnisko-balice} to stała cena"),
    ("route", "transfer-na-lotnisko-balice", "body_en", "## Why from €35?", "## Why is it cheaper?"),
    ("route", "transfer-na-lotnisko-balice", "body_de", "## Warum ab 35 €?", "## Warum günstiger?"),
    # Blog: stale prices -> live price tokens.
    ("blog", "ile-kosztuje-transfer-na-lotnisko-balice", "body_pl",
     "kosztuje od 149 zł", "kosztuje od {price:route:transfer-na-lotnisko-balice}"),
    ("blog", "ile-kosztuje-transfer-na-lotnisko-balice", "body_pl",
     "Sprawdź transfer na lotnisko Balice — 149 zł →",
     "Sprawdź transfer na lotnisko Balice — od {price:route:transfer-na-lotnisko-balice} →"),
    ("blog", "balice-zakopane-ile-kosztuje", "body_pl",
     "| Volkswagen Multivan | do 6 osób | **399 zł** |",
     "| Volkswagen Multivan | do 6 osób | **{price:route:balice-zakopane}** |"),
    ("blog", "balice-zakopane-ile-kosztuje", "body_pl",
     "Cena 399 zł obowiązuje", "Cena {price:route:balice-zakopane} obowiązuje"),
    ("blog", "auschwitz-birkenau-jak-zaplanowac-wycieczke", "body_pl",
     AUSCHWITZ_TABLE_OLD,
     "| Volkswagen Multivan | do 6 osób | **od {price:tour:auschwitz-birkenau-transfer247}** |"),
    ("blog", "kopalnia-soli-wieliczka-transfer-i-bilety", "body_pl",
     WIELICZKA_TABLE_OLD,
     "| Volkswagen Multivan | do 6 osób | **od {price:tour:wieliczka-transfer247}** |"),
    # Blog: leaked SEO notes + missing contextual links.
    ("blog", "krakow-airport-transfer-to-hotel-guide", "body_pl",
     "Turysta przylatujący na lotnisko Kraków Balice zwykle szuka prostego rozwiązania: **Krakow airport transfer to hotel**, **private transfer from Krakow Airport**, **Balice airport taxi to city centre** albo **transfer KRK airport to Old Town**. Dobra strona transferowa musi jasno odpowiadać na te pytania już w pierwszym widoku: skąd odbiór, dokąd jedziemy, czy kierowca mówi po angielsku, czy cena jest stała i czy można zarezerwować kurs przed przylotem.",
     "Po wylądowaniu na lotnisku Kraków Balice większość podróżnych chce po prostu szybko i bez stresu dotrzeć do hotelu w centrum, apartamentu na Kazimierzu albo na Stare Miasto. Przed rezerwacją warto sprawdzić kilka rzeczy: skąd dokładnie jest odbiór, czy kierowca mówi po angielsku, czy cena jest stała i czy kurs można zarezerwować jeszcze przed wylotem."),
    ("blog", "krakow-airport-transfer-to-hotel-guide", "body_pl",
     "transfer247.pl powinien dalej wzmacniać frazy angielskie, bo turyści nie szukają po polsku. Najważniejsze kombinacje to Krakow airport transfer, private airport transfer Krakow, Krakow Balice to hotel, Krakow airport to city centre, Krakow airport to Old Town oraz transfers from Krakow airport to Auschwitz, Wieliczka and Zakopane.",
     "Z lotniska Balice jeździmy nie tylko do centrum Krakowa: popularny jest też [transfer do Zakopanego](/transfery-lotniskowe/balice-zakopane), przejazd między lotniskami [Balice – Katowice](/transfery-lotniskowe/balice-katowice) oraz wycieczki do [Auschwitz-Birkenau](/wycieczki/auschwitz-birkenau-transfer247) i [Kopalni Soli Wieliczka](/wycieczki/wieliczka-transfer247)."),
    ("blog", "krakow-airport-transfer-to-hotel-guide", "body_pl",
     "## Jak odróżnić ofertę od konkurencji?", "## Jak wybrać dobrą ofertę transferu?"),
    ("blog", "krakow-airport-transfer-to-hotel-guide", "body_pl",
     "Konkurencja w Krakowie jest silna: duże firmy transferowe, portale rezerwacyjne, Tripadvisor, GetYourGuide i lokalne taxi. Przewaga transfer247.pl powinna być komunikowana konkretnie: stała cena, rezerwacja online, angielskojęzyczny kontakt, transfery 24/7, Balice i Katowice Pyrzowice, wycieczki do Auschwitz, Wieliczki, Zakopanego, Energylandii i na Spływ Dunajcem.",
     "W Krakowie wybór jest duży: firmy transferowe, portale rezerwacyjne, aplikacje i lokalne taxi. Porównując oferty, sprawdź, czy cena jest stała i podana z góry, czy można zarezerwować online i porozumieć się po angielsku oraz czy przewoźnik jeździ 24/7. W transfer247.pl to standard — obsługujemy lotniska Balice i Katowice-Pyrzowice, a także wycieczki do Auschwitz, Wieliczki, Zakopanego, Energylandii i na spływ Dunajcem."),
    ("blog", "katowice-pyrzowice-airport-to-krakow-transfer", "body_pl",
     "Dla SEO najważniejsze frazy to **Katowice Airport to Krakow transfer**, **Pyrzowice to Krakow private transfer**, **KTW airport to Krakow hotel**, **Katowice Pyrzowice airport taxi Krakow** oraz po polsku **transfer Katowice Pyrzowice Kraków**. Konkurencja często opisuje tylko cenę, ale turysta potrzebuje też informacji o czasie przejazdu, bagażu, odbiorze w nocy i bezpośrednim dojeździe pod hotel.",
     "Najprostsza odpowiedź to prywatny [transfer z lotniska Katowice-Pyrzowice do Krakowa](/transfery-lotniskowe/katowice-krakow): kierowca czeka w hali przylotów, zna numer Twojego lotu i jedzie autostradą A4 prosto pod hotel — zwykle w około 1 godzinę 30 minut. Cena jest stała, od {price:route:katowice-krakow} za cały bus do 6 osób, także przy nocnym przylocie. Jedziesz dalej w góry? Zobacz też [transfer z Krakowa do Zakopanego](/transfery/krakow-zakopane)."),
    ("blog", "katowice-pyrzowice-airport-to-krakow-transfer", "body_en",
     "The strongest search phrases are **Katowice Airport to Krakow transfer**, **Pyrzowice to Krakow private transfer**, **KTW airport to Krakow hotel** and **Katowice Pyrzowice airport taxi Krakow**. A private transfer is useful when passengers want one fixed pickup, space for luggage and a direct ride to the hotel.",
     "The simplest answer is a private [Katowice Airport to Krakow transfer](/transfery-lotniskowe/katowice-krakow): the driver meets you at arrivals, tracks your flight and takes the A4 motorway straight to your hotel — usually in about 1 hour 30 minutes. The price is fixed, from {price:route:katowice-krakow} for the whole van (up to 6 people), night arrivals included. Heading to the mountains? See our [Krakow to Zakopane transfer](/transfery/krakow-zakopane)."),
    # Pyrzowice guide: anchor "transfer z Pyrzowic do Krakowa" + CTA with live price.
    ("blog", "katowice-pyrzowice-jak-dojechac-do-krakowa", "body_pl",
     "Aktualną cenę pokazuje strona [transfer Katowice-Pyrzowice - Kraków](/transfery-lotniskowe/katowice-krakow). Cena dotyczy całego auta, nie osoby, więc przy kilku pasażerach koszt dzieli się na grupę.",
     "Prywatny [transfer z Pyrzowic do Krakowa](/transfery-lotniskowe/katowice-krakow) kosztuje od {price:route:katowice-krakow} za cały bus do 6 osób — cena jest stała, 24/7, bez dopłat nocnych. Dotyczy całego auta, nie osoby, więc przy kilku pasażerach koszt dzieli się na grupę.\n\n"
     "**[Zarezerwuj transfer Pyrzowice – Kraków od {price:route:katowice-krakow} →](/transfery-lotniskowe/katowice-krakow)**"),
    ("blog", "katowice-pyrzowice-jak-dojechac-do-krakowa", "body_en",
     "Krakow city centre or Krakow Balice Airport.",
     "Krakow city centre or [Krakow Balice Airport](/transfery-lotniskowe/balice-katowice)."),
    ("blog", "katowice-pyrzowice-jak-dojechac-do-krakowa", "body_en",
     "It is a price for the whole vehicle, not per passenger.",
     "It is a price for the whole vehicle, not per passenger — currently from {price:route:katowice-krakow} for up to 6 people."),
]

# --- Paragraphs inserted before a heading (first match of any listed) ------
INSERT_BEFORE = [
    # Prompt: H2 "Transfer na lotnisko Balice z Krakowa i okolic" on balice-krakow —
    # short, pointing at the dedicated (cheaper) drop-off page instead of
    # duplicating it, so the two pages don't compete for the same query.
    ("route", "balice-krakow", "body_pl", ["## Najczęściej zadawane pytania"],
     "## Transfer na lotnisko Balice z Krakowa i okolic\n\n"
     "Lecisz z Balic? Odbieramy Cię spod domu, hotelu lub apartamentu w Krakowie, Wieliczce, Skawinie czy "
     "Niepołomicach i jedziemy prosto pod terminal. Z centrum Krakowa to zwykle około 25 minut, ale w "
     "godzinach szczytu ruch potrafi wydłużyć przejazd — dlatego podstawiamy bus z zapasem: standardowo "
     "ok. 3 godziny przed wylotem w strefie Schengen i 3,5 godziny przed lotem poza nią.\n\n"
     "Dojazd na wylot nie wymaga śledzenia lotu ani czekania w hali przylotów, więc kosztuje mniej: "
     "[transfer na lotnisko Balice](/transfery-lotniskowe/transfer-na-lotnisko-balice) to stała cena od "
     "{price:route:transfer-na-lotnisko-balice} za cały bus do 6 osób, 24/7, bez dopłat za wczesne "
     "godziny.\n\n"),
    ("blog", "auschwitz-birkenau-jak-zaplanowac-wycieczke", "body_pl", ["## Jak wygląda dzień wycieczki"],
     "Szczegóły, zdjęcia i rezerwację znajdziesz na stronie [wycieczki do Auschwitz-Birkenau z "
     "Krakowa](/wycieczki/auschwitz-birkenau-transfer247). Przylatujesz dopiero do Krakowa? Zacznij od "
     "[transferu z lotniska Balice do hotelu](/transfery-lotniskowe/balice-krakow).\n\n"),
    ("blog", "kopalnia-soli-wieliczka-transfer-i-bilety", "body_pl", ["## Transfer z kierowcą czekającym"],
     "Szczegóły i rezerwację znajdziesz na stronie [wycieczki do Kopalni Soli Wieliczka z "
     "Krakowa](/wycieczki/wieliczka-transfer247). Wieliczkę łatwo połączyć z drugą wycieczką — wielu "
     "gości jedzie też do [Auschwitz-Birkenau](/wycieczki/auschwitz-birkenau-transfer247).\n\n"),
    ("blog", "transfer-z-lotniska-krakow-balice-kompletny-przewodnik-2026", "body_pl", ["## FAQ"],
     "Wylatujesz z Krakowa? Dojazd na wylot jest tańszy niż odbiór z lotniska — sprawdź "
     "[transfer na lotnisko Balice](/transfery-lotniskowe/transfer-na-lotnisko-balice) od "
     "{price:route:transfer-na-lotnisko-balice}.\n\n"),
    ("blog", "transfer-z-lotniska-krakow-balice-kompletny-przewodnik-2026", "body_en", ["## FAQ"],
     "Flying out of Krakow? A drop-off is cheaper than an airport pickup — see our "
     "[transfer to Krakow Balice Airport](/transfery-lotniskowe/transfer-na-lotnisko-balice) from "
     "{price:route:transfer-na-lotnisko-balice}.\n\n"),
    ("blog", "transfer-z-lotniska-krakow-balice-kompletny-przewodnik-2026", "body_de", ["## FAQ"],
     "Sie fliegen ab Krakau? Die Fahrt zum Abflug ist günstiger als die Abholung — siehe unseren "
     "[Transfer zum Flughafen Krakau-Balice](/transfery-lotniskowe/transfer-na-lotnisko-balice) ab "
     "{price:route:transfer-na-lotnisko-balice}.\n\n"),
]

# The PL version of this post was a 2-sentence stub (232 chars) under an
# English slug, while EN/DE carry a full article — translated from EN.
CLOSEST_AIRPORT_BODY_PL = (
    "Najbliższe duże lotniska do Muzeum Auschwitz-Birkenau to **Kraków-Balice (KRK)** i "
    "**Katowice-Pyrzowice (KTW)**. Oba sprawdzają się dobrze, a wybór zależy od godzin lotów, ceny "
    "biletów i tego, czy chcesz zwiedzać Kraków przed wizytą w Oświęcimiu, czy po niej.\n\n"
    "## Które lotnisko jest najbliżej Auschwitz?\n\n"
    "Z Pyrzowic do Oświęcimia jest drogowo często nieco bliżej, ale lotnisko w Balicach jest zwykle "
    "wygodniejsze, jeśli nocujesz w Krakowie albo chcesz połączyć Auschwitz z Wieliczką lub zwiedzaniem "
    "miasta. W obu przypadkach prywatny transfer oszczędza przesiadek z bagażem między pociągiem a "
    "autobusem.\n\n"
    "## Z lotniska Kraków-Balice do Auschwitz\n\n"
    "Balice to najczęstszy wybór osób, które nocują w Krakowie. Możesz zamówić [odbiór z lotniska do "
    "hotelu](/transfery-lotniskowe/balice-krakow), a na kolejny dzień zaplanować prywatną wycieczkę do "
    "Auschwitz z kierowcą, który czeka na miejscu.\n\n"
    "## Z lotniska Katowice-Pyrzowice do Auschwitz i Krakowa\n\n"
    "Pyrzowice przydają się, gdy loty są tańsze albo mają lepsze godziny. Wielu podróżnych po wizycie w "
    "Muzeum jedzie dalej do Krakowa albo od razu zamawia bezpośredni [transfer z Pyrzowic do "
    "Krakowa](/transfery-lotniskowe/katowice-krakow).\n\n"
    "## Zarezerwuj wycieczkę do Auschwitz-Birkenau\n\n"
    "Najprościej wybrać **prywatną wycieczkę do Auschwitz-Birkenau z Krakowa** z kierowcą czekającym na "
    "miejscu — bez dopasowywania się do rozkładów busów i pociągów. [Zarezerwuj wycieczkę do "
    "Auschwitz-Birkenau od {price:tour:auschwitz-birkenau-transfer247} →](/wycieczki/auschwitz-birkenau-transfer247)\n\n"
    "## FAQ\n\n"
    "**Które lotnisko jest najbliżej Auschwitz?**\n"
    "Praktycznie wchodzą w grę dwa: Katowice-Pyrzowice i Kraków-Balice. Z Katowic bywa drogowo nieco "
    "bliżej, a Kraków jest zwykle lepszy, jeśli nocujesz w mieście.\n\n"
    "**Czy mogę pojechać z lotniska w Balicach prosto do Auschwitz?**\n"
    "Tak, odbiór z lotniska można połączyć z wizytą w Muzeum.\n\n"
    "**Czy po wizycie w Auschwitz mogę pojechać dalej do Krakowa?**\n"
    "Tak, trasę planujemy z odbiorem, czasem oczekiwania i dowozem pod wskazany adres w Krakowie.\n\n"
    "**Czy bilety do Muzeum są wliczone w cenę transferu?**\n"
    "Nie, wejściówki i zwiedzanie z przewodnikiem rezerwuje się osobno w oficjalnym systemie Muzeum."
)


def _nl(text):
    return "\r\n" if "\r\n" in text else "\n"


def _replace(obj, field, old, new):
    body = getattr(obj, field) or ""
    nl = _nl(body)
    old, new = old.replace("\n", nl), new.replace("\n", nl)
    if old in body:
        setattr(obj, field, body.replace(old, new, 1))
        return True
    return False


def _insert_before(obj, field, headings, text):
    body = getattr(obj, field) or ""
    nl = _nl(body)
    marker = text.split("\n", 1)[0].strip()
    if marker and marker in body:
        return False  # already applied
    for heading in headings:
        match = re.search("^" + re.escape(heading), body, re.M)
        if match:
            setattr(obj, field, body[: match.start()] + text.replace("\n", nl) + body[match.start():])
            return True
    return False


LINK_RE = re.compile(r"\]\((/(?:transfery-lotniskowe|transfery|wycieczki)/[a-z0-9-]+)\)")


def _links_exist(apps, text):
    """Every internal route/tour link in `text` must point at an existing,
    correctly-filed page — otherwise the edit is skipped (same rule as
    InternalCmsLinkIntegrityTests), e.g. on a database where a route was
    only ever created through Admin."""
    FixedRoute = apps.get_model("content", "FixedRoute")
    Tour = apps.get_model("content", "Tour")
    for path in LINK_RE.findall(text):
        _, section, slug = path.split("/")
        if section == "wycieczki":
            ok = Tour.objects.filter(slug=slug).exists()
        else:
            routes = FixedRoute.objects.filter(slug=slug)
            ok = routes.filter(category="LOTNISKO").exists() if section == "transfery-lotniskowe" else routes.exclude(category="LOTNISKO").exists()
        if not ok:
            return False
    return True


def forwards(apps, schema_editor):
    models = {
        "route": apps.get_model("content", "FixedRoute"),
        "tour": apps.get_model("content", "Tour"),
        "blog": apps.get_model("content", "BlogPost"),
    }
    touched = {}

    def get(kind, slug):
        key = (kind, slug)
        if key not in touched:
            touched[key] = models[kind].objects.filter(slug=slug).first()
        return touched[key]

    for kind, table in (("route", ROUTE_SEO), ("tour", TOUR_SEO), ("blog", BLOG_SEO)):
        for slug, locales in table.items():
            obj = get(kind, slug)
            if obj is None:
                continue
            for locale, (title, description) in locales.items():
                if title:
                    setattr(obj, f"seo_title_{locale}", title)
                if description:
                    setattr(obj, f"seo_description_{locale}", description)

    for kind, slug, field, old, new in REPLACE:
        obj = get(kind, slug)
        if obj is not None and _links_exist(apps, new):
            _replace(obj, field, old, new)

    for kind, slug, field, headings, text in INSERT_BEFORE:
        obj = get(kind, slug)
        if obj is not None and _links_exist(apps, text):
            _insert_before(obj, field, headings, text)

    post = get("blog", "closest-airport-to-auschwitz")
    if post is not None and len((post.body_pl or "").strip()) < 600 and _links_exist(apps, CLOSEST_AIRPORT_BODY_PL):
        post.body_pl = CLOSEST_AIRPORT_BODY_PL

    for obj in touched.values():
        if obj is not None:
            obj.save()  # auto_now also stamps updated_at


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0068_updated_at_for_sitemap"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
