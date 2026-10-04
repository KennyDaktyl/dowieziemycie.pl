# transfer247.pl: EN/DE route bodies with their Markdown back, EN tour bodies.
#
# - 8 EN/DE FixedRoute bodies had been translated from the rendered page and
#   pasted into Admin as plain text: no ## headings, no FAQ markup (so no
#   FAQPage), no internal links. Rebuilt as proper Markdown translations of
#   the current PL body (same sections, FAQ and links). DE balice-zakopane
#   follows the PL text extended in 0074.
# - Auschwitz-Birkenau and Wieliczka tours had an empty body_en, so their EN
#   pages were noindex (translatedLocales needs title + body). Full EN bodies
#   added; practical facts (distances, Memorial/Mine visiting rules) are kept
#   general and point to the official booking sites.
#
# Same guard as 0074: a field is overwritten only if its current value is the
# one seen in production (or empty), so Admin edits made since are skipped.
# Not reversible in content terms — backwards is a no-op.

import hashlib

from django.db import migrations

EMPTY = "e3b0c44298fc1c14"

# --- FixedRoute: balice-krakow ------------------------------------------------

BALICE_KRAKOW_DE = """Privater Flughafentransfer ab Krakau-Balice – ins Stadtzentrum, zum Hotel, Apartment oder Bahnhof. Ihr Fahrer wartet in der Ankunftshalle, wir verfolgen Ihre Flugnummer und fahren Sie direkt zur gewünschten Adresse.

## Flughafentransfer Krakau-Balice rund um die Uhr

Ihr Fahrer erwartet Sie in der Ankunftshalle mit einem Namensschild – zu jeder Tageszeit, auch nachts. Der Preis hängt vom gewählten Fahrzeug ab und steht vor der Buchung in der Tabelle oben.

## Flughafen Balice – Hotel in Krakau

Wir holen Sie am Terminal KRK ab und bringen Sie zu Ihrem Hotel, Apartment, einer Privatadresse, zum Bahnhof oder an jeden anderen Ort in Krakau. Diese Strecke ist die Abholung **vom** Flughafen – wenn Sie **zum** Abflug fahren, sehen Sie sich unser günstigeres Angebot an: [Transfer zum Flughafen Balice](/transfery-lotniskowe/transfer-na-lotnisko-balice), ohne Flugverfolgung.

## Transfer zum Flughafen Balice aus Krakau und Umgebung

Sie fliegen ab Balice? Wir holen Sie zu Hause, im Hotel oder Apartment in Krakau, Wieliczka, Skawina oder Niepołomice ab und fahren direkt zum Terminal. Aus dem Zentrum von Krakau sind es meist etwa 25 Minuten, in der Hauptverkehrszeit kann es länger dauern – deshalb kommen wir mit Zeitpuffer: standardmäßig etwa 3 Stunden vor einem Schengen-Flug und 3,5 Stunden vor einem Flug außerhalb des Schengen-Raums.

Die Fahrt zum Abflug braucht weder Flugverfolgung noch Wartezeit in der Ankunftshalle und kostet daher weniger: Der [Transfer zum Flughafen Balice](/transfery-lotniskowe/transfer-na-lotnisko-balice) hat einen Festpreis ab {price:route:transfer-na-lotnisko-balice} für den ganzen Van bis 6 Personen, rund um die Uhr, ohne Zuschlag für frühe Stunden.

## Häufig gestellte Fragen

**Wie lange dauert der Transfer vom Flughafen Balice nach Krakau?**
Meist etwa 25 Minuten bis ins Zentrum, je nach Verkehr.

**Verfolgt der Fahrer meinen Flug?**
Ja, Sie geben Ihre Flugnummer an, und bei einer Verspätung passen wir die Abholzeit an.

**Kann ich einen Transfer von Krakau zum Flughafen Balice buchen?**
Ja, die Strecke gilt in beide Richtungen. Wenn Sie ab Balice abfliegen (und nicht ankommen), nutzen Sie unser günstigeres Angebot: [Transfer zum Flughafen Balice](/transfery-lotniskowe/transfer-na-lotnisko-balice) – ohne Flugverfolgung und Wartezeit am Terminal, daher günstiger.

**Ist der Transfer privat?**
Ja, Sie fahren nur mit den Personen aus Ihrer Buchung.

## Weitere Informationen

Einen praktischen Überblick über alle Möglichkeiten – Festpreis, Flugverfolgung, Gruppen bis 6 Personen, Fahrradtransport und weitere Strecken – finden Sie in unserem [Ratgeber zum Flughafentransfer Krakau-Balice (2026)](/blog/transfer-z-lotniska-krakow-balice-kompletny-przewodnik-2026)."""

# --- FixedRoute: katowice-krakow ----------------------------------------------

KATOWICE_KRAKOW_DE = """Den Transfer vom Flughafen Katowice-Pyrzowice nach Krakau führen wir mit einem privaten Fahrzeug durch – ohne Umsteigen und ohne andere Fahrgäste. Der Fahrer holt Sie am Terminal ab, verfolgt Ihren Flug und fährt direkt zu Ihrer Adresse in Krakau.

## Transfer Pyrzowice – Krakau: Preis und Fahrzeit

Die Fahrt über die A4 dauert meist etwa **1 Stunde 30 Minuten**. Der aktuelle Preis hängt vom gewählten Fahrzeug ab und steht vor der Buchung in der Tabelle oben. Der Preis gilt für das ganze Fahrzeug, nicht pro Person, und rund um die Uhr – auch bei Nachtankünften.

## Bus, Zug oder privater Transfer?

| Option | Fahrzeit | Komfort | Wann sinnvoll |
|---|---|---|---|
| Bus Pyrzowice – Krakau | meist 2 h oder mehr | Fahrplan, feste Haltestelle | eine Person, wenig Gepäck |
| Zug mit Umstieg | meist 2,5–3 h | Umstieg nötig | wenn Zeit keine Rolle spielt |
| Privater Transfer | etwa 1 h 30 min | Abholung am Terminal, Fahrt bis zur Tür | Familie, Gruppe, Nachtflug, Gepäck |

## Abholung am Flughafen Katowice-Pyrzowice

Nach der Buchung geben Sie Ihre Flugnummer an. Der Fahrer verfolgt die Ankunft und wartet in der Ankunftshalle mit einem Namensschild. Bei einer Verspätung wird die Abholzeit ohne Aufpreis angepasst.

## Bis zum Hotel, Apartment oder zum Flughafen Balice

Der Transfer endet an Ihrer Adresse in Krakau: Hotel, Apartment, Bahnhof, Büro oder – beim Umsteigen – am Flughafen Krakau-Balice. Für die Gegenrichtung, von Krakau nach Pyrzowice, nutzen Sie dieselbe Seite und geben bei der Buchung die umgekehrte Richtung an.

## Häufig gestellte Fragen

**Wie lange dauert der Transfer von Pyrzowice nach Krakau?**
Meist etwa 1 Stunde 30 Minuten, je nach Verkehr auf der A4.

**Ändert sich der Preis nachts?**
Nein, der Preis aus der Tabelle gilt rund um die Uhr, ohne Nachtzuschlag.

**Kann ich einen Van von Pyrzowice nach Krakau für eine größere Gruppe buchen?**
Ja, wählen Sie in der Preistabelle ein größeres Fahrzeug, sofern es für diese Strecke verfügbar ist.

**Wartet der Fahrer bei einer Flugverspätung?**
Ja, wir verfolgen die Flugnummer und passen die Abholzeit an.

**Ist der Transfer privat?**
Ja, Sie fahren nur mit den Personen aus Ihrer Buchung.

**Kann ich von Krakau zum Flughafen Katowice-Pyrzowice fahren?**
Ja, die Strecke gilt in beide Richtungen."""

# --- FixedRoute: balice-zakopane (follows the PL body from 0074) -------------

BALICE_ZAKOPANE_DE = """Der Transfer vom Flughafen Krakau-Balice nach Zakopane gehört zu den beliebtesten Fahrten für Reisende, die in Kleinpolen landen und in die Tatra wollen. Die Strecke ist etwa 100 km lang und dauert normalerweise 1 Stunde 45 Minuten bis 2 Stunden. Sie fahren in einem privaten Volkswagen Multivan – ohne Umsteigen, direkt vom Terminal bis vor Ihr Hotel, Ihre Pension oder Ihr Apartment.

## Was kostet der Transfer Balice – Zakopane?

Ein Festpreis ab {price} für das ganze Fahrzeug, nicht pro Person – der Volkswagen Multivan bringt bis zu 6 Personen mit Gepäck. Der Preis gilt rund um die Uhr: ohne Nacht-, Wochenend- oder Ferienzuschlag. Die aktuelle Preisliste steht in der Tabelle oben, die Verfügbarkeit sehen Sie sofort im Buchungsformular.

## Die Strecke: S7 und Zakopianka

Vom Flughafen fahren wir über die Krakauer Ringstraße, dann auf der Schnellstraße S7 über Myślenice und Lubień bis Rabka und ab Rabka auf der Landesstraße 47 – der „Zakopianka“ – über Nowy Targ nach Zakopane. Unsere Fahrer kennen die Strecke und die Umfahrungen, auch im Winter.

## Staus am Wochenende – wann fahren?

Am meisten Zeit verliert man freitagnachmittags (Richtung Zakopane), sonntagnachmittags und -abends (Richtung Krakau) sowie bei der Einfahrt nach Zakopane in den Winterferien und an langen Wochenenden. In der Skisaison buchen Sie am besten einige Tage im Voraus und planen für die Rückfahrt zum Flughafen mehr Zeit ein. Wir verfolgen Ihre Flugnummer – bei einer Verspätung passen wir die Abholzeit ohne Aufpreis an.

## Ein Halt unterwegs

Die Fahrt dauert etwa 2 Stunden, daher können wir auf Wunsch unterwegs kurz anhalten – für die Toilette, einen Kaffee oder einen Einkauf. Vermerken Sie das einfach in den Buchungsnotizen.

## Ski, Snowboard und Wintergepäck

Der Multivan bietet bequem Platz für 6 Personen mit Koffern sowie Ski oder Snowboards in Taschen. Wenn Sie als volle Gruppe mit sperriger Winterausrüstung reisen, vermerken Sie das in den Buchungsnotizen – wir bestätigen, dass alles hineinpasst. Das Fahrzeug ist für winterliche Bedingungen ausgerüstet.

## Nacht- und Frühfahrten

Sie landen spätabends oder nachts? Wir holen Sie zu jeder Uhrzeit am Flughafen Balice ab, zum gleichen Preis – ohne Nachtzuschlag. Für einen frühen Rückflug holen wir Sie in Zakopane mit ausreichend Zeit für den Check-in ab.

## So läuft die Abholung am Flughafen

1. Nach der Buchung geben Sie Ihre Flugnummer an – das System verfolgt sie automatisch.
2. Der Fahrer wartet in der Ankunftshalle mit einem Schild mit Ihrem Namen.
3. Sie fahren direkt zu Ihrer Adresse in Zakopane – Hotel, Pension oder Apartment.

## Sicherheit und Kindersitze

Jeder Transfer ist privat, in einem versicherten Fahrzeug, ohne andere Fahrgäste. Einen Kindersitz stellen wir auf Wunsch kostenlos – einfach im Buchungsformular auswählen.

## So buchen Sie

Sie buchen online in wenigen Minuten: Strecke und Fahrzeug wählen, Telefonnummer per SMS-Code bestätigen und nach der Bestätigung durch unseren Disponenten die Anzahlung leisten. Fahrtstatus und Standort des Fahrers verfolgen Sie live auf der Karte.

## Stornierung und Änderungen

Eine Stornierung ist immer kostenlos und jederzeit selbst im Kundenbereich möglich – ohne Anruf oder E-Mail.

## Weitere Strecken ab Flughafen Balice

Neben Zakopane fahren wir ins Zentrum von Krakau, nach Wieliczka, Katowice und zum Freizeitpark Energylandia – sehen Sie sich [alle Strecken](/transfery) an oder den [Flughafentransfer Krakau ins Stadtzentrum](/transfery-lotniskowe/balice-krakow).

## Häufig gestellte Fragen

**Ändert sich der Preis für Balice – Zakopane nachts?**
Nein, der Preis aus der Tabelle oben gilt rund um die Uhr, unabhängig von der Abholzeit.

**Was passiert, wenn mein Flug Verspätung hat?**
Wir verfolgen Ihre Flugnummer und passen die Abholzeit kostenlos an.

**Wie lange dauert die Fahrt von Balice nach Zakopane?**
Meist 1 Stunde 45 Minuten bis 2 Stunden, je nach Verkehr und Jahreszeit. Freitags, sonntags und in den Winterferien kann es länger dauern.

**Ist der Transfer privat?**
Ja, immer privat – Sie fahren nur mit den Personen aus Ihrer Buchung.

**Passen Ski und Wintergepäck hinein?**
Ja, der Multivan bietet Platz für 6 Personen mit Koffern und Ski in Taschen. Reisen Sie als volle Gruppe mit sperriger Ausrüstung, vermerken Sie das in den Buchungsnotizen.

**Können wir unterwegs anhalten?**
Ja, auf Wunsch halten wir kurz an – vermerken Sie das einfach in den Buchungsnotizen.

**Holen Sie mich nachts am Flughafen ab?**
Ja, wir fahren rund um die Uhr, und der Nachtpreis ist derselbe wie tagsüber.

**Ist ein Kindersitz im Preis enthalten?**
Ja, auf Wunsch und kostenlos.

**Kann ich den Transfer auch in Gegenrichtung buchen, von Zakopane zum Flughafen?**
Ja, Strecke und Bedingungen gelten in beide Richtungen.

**Kann ich meine Buchung stornieren?**
Ja, die Stornierung ist immer kostenlos und selbst im Kundenbereich möglich."""

# --- FixedRoute: balice-katowice ----------------------------------------------

BALICE_KATOWICE_EN = """We run the transfer from Kraków-Balice Airport to Katowice in a private vehicle, never shared with other passengers. The price in the table above applies around the clock, seven days a week, whichever vehicle you choose.

## How much is the Balice – Katowice transfer and how long does it take?

The drive takes about 1 hour 20 minutes, depending on traffic on the A4 motorway. The price is fixed whatever the pickup time — you don't pay more for a night or weekend ride.

## Who books this transfer?

It's a popular ride for travellers who land in Kraków-Balice but are heading on to Silesia — a business meeting, an event in Katowice, or an onward train from Katowice station.

## How the pickup works

1. After booking, you give us your flight number — we track it automatically.
2. Your driver waits in the arrivals hall with a sign with your name.
3. You're driven directly to your address in Katowice.

## Safety

Every transfer is private, in an insured vehicle. A child seat is provided free of charge on request — just select it in the booking form.

## How to book

Choose the vehicle and date, confirm your phone number with an SMS code, and once our dispatcher confirms the booking, pay the deposit online. You can pay the rest at any time before the ride.

## Other routes from Kraków-Balice Airport

Besides Katowice, we run transfers to Kraków city centre, Zakopane, Wieliczka and Energylandia — see [all our routes](/transfery).

## Frequently asked questions

**Does the price change at night?**
No, the price in the table above applies 24 hours a day, whatever the pickup time.

**What if my flight is delayed?**
We track your flight number and adjust the pickup time free of charge.

**How long is the ride from Balice to Katowice?**
Usually about 1 hour 20 minutes, depending on traffic on the A4.

**Is the transfer private?**
Yes, always — only you and the people in your booking travel with you.

**Can I book the transfer the other way, from Katowice to Balice?**
Yes, the same route and terms apply in both directions.

**Can I cancel my booking?**
Yes, cancellation is always free and you can do it yourself in the client panel."""

BALICE_KATOWICE_DE = """Den Transfer vom Flughafen Krakau-Balice nach Katowice führen wir mit einem privaten Fahrzeug durch, ohne andere Fahrgäste. Der Preis in der Tabelle oben gilt rund um die Uhr, sieben Tage die Woche, unabhängig vom gewählten Fahrzeug.

## Was kostet und wie lange dauert der Transfer Balice – Katowice?

Die Fahrt dauert etwa 1 Stunde 20 Minuten, je nach Verkehr auf der Autobahn A4. Der Preis ist unabhängig von der Abholzeit fest – für Nacht- oder Wochenendfahrten zahlen Sie nicht mehr.

## Wer nutzt diesen Transfer?

Eine beliebte Fahrt für Reisende, die in Balice landen, aber weiter nach Schlesien wollen – zu einem Geschäftstermin, einer Veranstaltung in Katowice oder zur Weiterreise mit dem Zug ab dem Bahnhof Katowice.

## So läuft die Abholung

1. Nach der Buchung geben Sie Ihre Flugnummer an – wir verfolgen sie automatisch.
2. Der Fahrer wartet in der Ankunftshalle mit einem Schild mit Ihrem Namen.
3. Sie fahren direkt zu Ihrer Adresse in Katowice.

## Sicherheit

Jeder Transfer ist privat, in einem versicherten Fahrzeug. Einen Kindersitz stellen wir auf Wunsch kostenlos – einfach im Buchungsformular auswählen.

## So buchen Sie

Wählen Sie Fahrzeug und Datum, bestätigen Sie Ihre Telefonnummer per SMS-Code und leisten Sie nach der Bestätigung durch den Disponenten die Anzahlung online. Den Rest können Sie jederzeit vor der Fahrt bezahlen.

## Weitere Strecken ab Flughafen Balice

Neben Katowice fahren wir ins Zentrum von Krakau, nach Zakopane, Wieliczka und zum Energylandia – sehen Sie sich [alle Strecken](/transfery) an.

## Häufig gestellte Fragen

**Ändert sich der Preis nachts?**
Nein, der Preis aus der Tabelle oben gilt rund um die Uhr, unabhängig von der Abholzeit.

**Was passiert, wenn mein Flug Verspätung hat?**
Wir verfolgen Ihre Flugnummer und passen die Abholzeit kostenlos an.

**Wie lange dauert die Fahrt von Balice nach Katowice?**
Meist etwa 1 Stunde 20 Minuten, je nach Verkehr auf der A4.

**Ist der Transfer privat?**
Ja, immer – Sie fahren nur mit den Personen aus Ihrer Buchung.

**Kann ich den Transfer auch in Gegenrichtung buchen, von Katowice nach Balice?**
Ja, Strecke und Bedingungen gelten in beide Richtungen.

**Kann ich meine Buchung stornieren?**
Ja, die Stornierung ist immer kostenlos und selbst im Kundenbereich möglich."""

# --- FixedRoute: dworzec-energylandia -----------------------------------------

DWORZEC_ENERGYLANDIA_EN = """Energylandia in Zator is the largest amusement park in Poland and one of the most popular attractions near Kraków — dozens of roller coasters and water attractions in one place. A transfer from Kraków to Energylandia is an easy alternative to the train or a bus with changes: we pick you up at your hotel or the station and drop you off at the park entrance.

## How long does it take from Kraków to Energylandia?

Energylandia is in Zator, about 70 km from Kraków — the drive usually takes about an hour, depending on traffic. Transfer247.pl drives you in a private vehicle, never shared with other passengers — straight to the park, with no stops on the way.

## Price of the Energylandia transfer

The fixed price shown above covers the ride from, for example, Kraków Główny station or your apartment or hotel to the Energylandia entrance — it doesn't depend on the time of day or the day of the week. Ask about a pickup after your visit when you book, or choose our [Kraków – Energylandia day trip](/wycieczki/krakow-energylandia) with the return journey included.

## Taking bikes to Energylandia

Bringing a bike? Our vehicle has a Thule VeloSpace bike carrier (4-bike version), so you can take your bikes for a ride around the area. The price for bikes is agreed individually when you book — see [bike transport](/przewoz-rowerow) for details.

## Why book a transfer

No changes, a fixed price known in advance, and a driver waiting at the agreed spot by the station. A good choice for families with children and groups who don't want to lose time on public transport.

## FAQ

**Does the transfer go right to the park entrance?**
Yes, we drop you off as close to the main entrance of Energylandia as possible.

**Can I bring a bike?**
Yes, the vehicle has a Thule VeloSpace carrier for 4 bikes — the price for bike transport is agreed individually when you book.

**Does the price change at weekends or in high season?**
No, the price shown above applies all year round, whatever the day of the week."""

DWORZEC_ENERGYLANDIA_DE = """Energylandia in Zator ist der größte Freizeitpark Polens und eine der beliebtesten Attraktionen rund um Krakau – Dutzende Achterbahnen und Wasserattraktionen auf einem Gelände. Ein Transfer von Krakau zum Energylandia ist die bequeme Alternative zu Zug oder Bus mit Umsteigen: Wir holen Sie direkt am Hotel oder Bahnhof ab und setzen Sie am Parkeingang ab.

## Wie lange dauert die Fahrt von Krakau zum Energylandia?

Energylandia liegt in Zator, etwa 70 km von Krakau entfernt – die Fahrt dauert meist etwa eine Stunde, je nach Verkehr. Transfer247.pl fährt Sie in einem privaten Fahrzeug, ohne andere Fahrgäste – direkt zum Ziel, ohne Zwischenhalte.

## Preis für den Transfer zum Energylandia

Der Festpreis oben gilt für die Fahrt z. B. vom Hauptbahnhof Krakau oder von Ihrem Apartment oder Hotel bis zum Eingang des Energylandia – unabhängig von Tageszeit und Wochentag. Fragen Sie bei der Buchung nach einer Abholung nach dem Parkbesuch.

## Fahrradtransport zum Energylandia

Sie reisen mit Fahrrad? Unser Fahrzeug hat einen Fahrradträger Thule VeloSpace (für 4 Räder) – so können Sie Ihre Räder für Touren in der Umgebung mitnehmen. Der Preis für den Fahrradtransport wird bei der Buchung individuell vereinbart – Details unter [Fahrradtransport](/przewoz-rowerow).

## Warum einen Transfer buchen

Kein Umsteigen, ein vorab bekannter Festpreis und ein Fahrer, der am vereinbarten Treffpunkt am Bahnhof wartet. Ideal für Familien mit Kindern und Gruppen, die keine Zeit mit öffentlichen Verkehrsmitteln verlieren möchten.

## FAQ

**Fährt der Transfer direkt bis zum Parkeingang?**
Ja, wir setzen Sie so nah wie möglich am Haupteingang des Energylandia ab.

**Kann ich ein Fahrrad mitnehmen?**
Ja, das Fahrzeug hat einen Thule-VeloSpace-Träger für 4 Fahrräder – der Preis für den Transport wird bei der Buchung individuell vereinbart.

**Ändert sich der Preis am Wochenende oder in der Saison?**
Nein, der Preis oben gilt das ganze Jahr, unabhängig vom Wochentag."""

# --- FixedRoute: dworzec-balice -----------------------------------------------

DWORZEC_BALICE_DE = """Der Transfer vom Hauptbahnhof Krakau (Kraków Główny) zum Flughafen Krakau-Balice ist die einfachste Antwort auf die Frage, wie man vom Bahnhof zum Flughafen kommt. Wir holen Sie an einem vereinbarten Treffpunkt am Bahnhof ab und fahren direkt zum Terminal.

## Hauptbahnhof – Balice: Fahrzeit

Die Fahrt dauert meist **25–30 Minuten**, je nach Verkehr im Zentrum von Krakau. Planen Sie vor dem Abflug genug Zeit für Check-in, Sicherheitskontrolle und den Weg zum Gate ein.

## Preis für den Transfer zum Flughafen Balice

Den aktuellen Preis sehen Sie in der Tabelle oben. Es ist ein Preis pro Fahrzeug, nicht pro Person – ohne Zuschläge für Nacht, Wochenende oder normales Gepäck.

## Wo treffe ich den Fahrer am Bahnhof?

Geben Sie bei der Buchung einen konkreten Abholpunkt an: den Ausgang zur Pawia-Straße, ein Hotel neben dem Bahnhof, einen Parkplatz oder eine andere Adresse, an der man gut halten kann. So muss der Fahrer nicht suchen, und Sie sind schneller unterwegs zum Flughafen.

## Häufig gestellte Fragen

**Wie lange fährt man vom Hauptbahnhof zum Flughafen Balice?**
Meist 25–30 Minuten, je nach Verkehr.

**Erfolgt die Abholung direkt am Bahnhof?**
Ja, den genauen Abholpunkt vereinbaren wir bei der Buchung.

**Ändert sich der Preis nachts?**
Nein, der Preis aus der Tabelle gilt rund um die Uhr.

**Kann ich auch einen Transfer vom Flughafen Balice zum Bahnhof buchen?**
Ja, die Strecke gilt in beide Richtungen."""

# --- Tour: auschwitz-birkenau-transfer247 -------------------------------------

AUSCHWITZ_EN = """Our Auschwitz-Birkenau tour from Kraków is a private return transfer with a driver who waits for you on site for the whole visit — no rush and no tour group. You travel only with the people in your booking, in a Volkswagen Multivan for up to 6 passengers.

## Price and duration

The trip takes up to 6 hours. The fixed price from {price} covers the return journey and the driver's waiting time, for the whole vehicle — not per person. Entry to the Memorial is booked separately (see below).

## How the day works

1. We pick you up from your hotel, apartment or Kraków Airport at the time you choose.
2. The drive to Oświęcim takes about 1 hour 15 minutes to 1 hour 30 minutes each way (around 70 km).
3. You visit Auschwitz I and Auschwitz II-Birkenau. The two sites are about 3 km apart and the Memorial runs a shuttle bus between them.
4. After the visit, the driver takes you back to your hotel in Kraków or straight to the airport.

## Entry passes and guided visits

Entry to the Auschwitz-Birkenau Memorial must be booked in advance for a specific time on the official website, visit.auschwitz.org. Most visitors join a tour with a Memorial educator (a paid guided visit, available in many languages); at certain times you can also enter without a guide. Places sell out in high season, so book your entry first and then choose the pickup time to match it — we'll plan the departure so you arrive on time.

## Practical tips

- Allow about 3.5 hours for a guided visit of both sites.
- The Museum only admits small bags; larger bags and luggage can stay in the vehicle, as your driver waits for you.
- Much of Birkenau is outdoors — wear comfortable shoes and dress for the weather.
- It's a place of remembrance: please dress and behave respectfully.

## Why a private transfer

The timing fits your entry slot rather than a group schedule, you're picked up at your door, and you can travel back at your own pace after a demanding visit. A child seat is available free of charge on request.

## Frequently asked questions

**Are entry tickets included in the price?**
No. The price covers transport and the driver's waiting time; entry to the Memorial is booked separately at visit.auschwitz.org.

**Does the driver wait on site?**
Yes, the driver stays nearby for the whole visit and drives you back afterwards.

**How long is the drive from Kraków to Auschwitz?**
About 1 hour 15 minutes to 1 hour 30 minutes each way, depending on traffic.

**Can you pick us up from Kraków Airport?**
Yes, we can collect you from Kraków-Balice and bring you back to your hotel or the airport after the visit.

**How many people can travel?**
Up to 6 passengers in the Volkswagen Multivan. The price is per vehicle, not per person.

**Can I cancel my booking?**
Yes, cancellation is always free and you can do it yourself in the client panel.

## More information

Flying in for the visit? Read which airport is [closest to Auschwitz](/blog/closest-airport-to-auschwitz), or book a [Krakow Airport transfer](/transfery-lotniskowe/balice-krakow) to your hotel."""

# --- Tour: wieliczka-transfer247 ----------------------------------------------

WIELICZKA_EN = """Our Wieliczka Salt Mine tour from Kraków is a private return transfer with a driver who waits for you on site for the whole visit. You travel only with the people in your booking, in a Volkswagen Multivan for up to 6 passengers.

## Price and duration

The trip takes up to 4 hours. The fixed price from {price} covers the return journey and the driver's waiting time, for the whole vehicle — not per person. Mine tickets are bought separately (see below).

## How the trip works

1. We pick you up from your hotel, apartment or Kraków Airport at the time you choose.
2. Wieliczka is about 15 km from the centre of Kraków — usually a 25–35 minute drive.
3. You tour the mine with a guide; the driver waits nearby.
4. After the visit, the driver takes you back to your hotel or on to your next stop.

## Tickets and the Tourist Route

The mine can only be visited with a guide, at set start times, and tours in English run throughout the day. Buy your tickets in advance on the official website, wieliczka-saltmine.com — in high season the popular times sell out — and choose the pickup time to match your tour. The Tourist Route takes about 3 hours.

## Practical tips

- Expect around 800 steps on the route, including about 380 going down at the start; you return to the surface by lift.
- It's about 17–18°C underground all year — bring a light jacket, even in summer.
- Wear comfortable shoes.

## Why a private transfer

The timing fits your tour slot, you're picked up at your door, and there's no waiting for a bus back. A good choice for families and groups of up to 6. A child seat is available free of charge on request.

## Frequently asked questions

**Are entry tickets included in the price?**
No. The price covers transport and the driver's waiting time; mine tickets are bought separately at wieliczka-saltmine.com.

**Does the driver wait on site?**
Yes, the driver stays nearby for the whole visit and drives you back afterwards.

**How long is the drive from Kraków to Wieliczka?**
Usually 25–35 minutes, depending on traffic.

**Can you pick us up from Kraków Airport?**
Yes, we can collect you from Kraków-Balice and bring you to your hotel after the visit.

**How many people can travel?**
Up to 6 passengers in the Volkswagen Multivan. The price is per vehicle, not per person.

**Can I cancel my booking?**
Yes, cancellation is always free and you can do it yourself in the client panel.

## More information

Arriving by plane? Book a [Krakow Airport transfer](/transfery-lotniskowe/balice-krakow) to your hotel, or see our [Auschwitz-Birkenau tour from Kraków](/wycieczki/auschwitz-birkenau-transfer247)."""

# (model, slug, field) -> (new value, fingerprints of the values it may replace)
FIELDS = {
    ("route", "balice-krakow", "body_de"): (BALICE_KRAKOW_DE, {"8d8395ab1f47fbac", EMPTY}),
    ("route", "katowice-krakow", "body_de"): (KATOWICE_KRAKOW_DE, {"7b1eb60d80c59e70", EMPTY}),
    ("route", "balice-zakopane", "body_de"): (BALICE_ZAKOPANE_DE, {"40e88b15d2929f64", EMPTY}),
    ("route", "balice-katowice", "body_en"): (BALICE_KATOWICE_EN, {"6e656db875e3caef", EMPTY}),
    ("route", "balice-katowice", "body_de"): (BALICE_KATOWICE_DE, {"1dd17495047145b7", EMPTY}),
    ("route", "dworzec-energylandia", "body_en"): (DWORZEC_ENERGYLANDIA_EN, {"c9ca9f74c91f0f4d", EMPTY}),
    ("route", "dworzec-energylandia", "body_de"): (DWORZEC_ENERGYLANDIA_DE, {"a74ffe7f3d2c54f3", EMPTY}),
    ("route", "dworzec-balice", "body_de"): (DWORZEC_BALICE_DE, {"ba8259c69ab9c15f", EMPTY}),
    ("tour", "auschwitz-birkenau-transfer247", "body_en"): (AUSCHWITZ_EN, {EMPTY}),
    ("tour", "wieliczka-transfer247", "body_en"): (WIELICZKA_EN, {EMPTY}),
}


def _fingerprint(text):
    return hashlib.sha256((text or "").replace("\r\n", "\n").strip().encode()).hexdigest()[:16]


def forwards(apps, schema_editor):
    models = {
        "route": apps.get_model("content", "FixedRoute"),
        "tour": apps.get_model("content", "Tour"),
    }
    objects = {}
    for (kind, slug, field), (new, expected) in FIELDS.items():
        key = (kind, slug)
        if key not in objects:
            objects[key] = models[kind].objects.filter(slug=slug).first()
        obj = objects[key]
        if obj is not None and _fingerprint(getattr(obj, field)) in expected:
            setattr(obj, field, new)
    for obj in objects.values():
        if obj is not None:
            obj.save()  # auto_now also stamps updated_at


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0074_transfer247_seo_airport_taxi_zakopane"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
