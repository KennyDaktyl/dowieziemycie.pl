# dowieziemycie.pl — Panel kierowcy (Expo / React Native)

Natywna aplikacja Android dla kierowców: logowanie (login + hasło, to samo
konto co `Driver.user` w Adminie), status w czasie rzeczywistym, wysyłanie
pozycji GPS w tle (działa nawet przy zgaszonym ekranie — foreground
service z widocznym powiadomieniem, zgodnie z wymaganiami Androida), lista
nowych kursów do przyjęcia, powiadomienia push o nowych kursach, oraz
harmonogram dnia.

## Dlaczego natywna appka, nie strona WWW

Przeglądarka usypia JavaScript, gdy ekran jest zgaszony albo aplikacja
przechodzi w tło — geolokalizacja i WebSocket przestają działać. Ta appka
używa Androidowego "foreground service" (ten sam mechanizm co Uber/Bolt),
który explicite wolno trzymać aktywnym w tle, właśnie do lokalizacji.

## Architektura

- **Logowanie**: `POST /api/fleet/driver/login/` (login+hasło) → JWT,
  zapisywany w `expo-secure-store` (zaszyfrowany magazyn systemowy, nie
  zwykły storage).
- **Pozycja w tle**: `expo-location` + `expo-task-manager` — zadanie w tle
  co ~10s robi zwykły `POST /api/fleet/driver/position/` (REST, nie
  WebSocket — Androidowy "headless" kontekst wykonania zadań w tle nie
  nadaje się do trzymania stałego połączenia WS, ale pojedynczy fetch()
  działa niezawodnie). Backend i tak rozgłasza tę pozycję przez
  WebSocket dalej do stron WWW (publiczna mapa, prywatne śledzenie
  klienta) — czas rzeczywisty po stronie oglądających jest zachowany
  niezależnie od tego, którym kanałem kierowca zgłosił pozycję.
- **Powiadomienia push**: `expo-notifications`, token rejestrowany przez
  `POST /api/fleet/driver/push-token/`. Backend wysyła push przez Expo Push
  Service (`apps/fleet/push.py`) przy każdej nowej rezerwacji.

## Uruchomienie lokalnie (podgląd bez budowania APK)

```sh
cd mobile
npm install
cp .env.example .env   # ustaw EXPO_PUBLIC_API_BASE_URL jeśli inny niż produkcja
npx expo start
```

**Uwaga**: śledzenie w tle (`expo-location` background) **nie działa** w
zwykłej aplikacji Expo Go ze sklepu — wymaga "development build" (patrz
niżej). Do podglądu samego UI/logowania/listy kursów Expo Go wystarczy.

## Zbudowanie prawdziwego APK (potrzebne do realnego testu na telefonie)

Tego kroku nie mogłem wykonać z tego środowiska — nie mam tu Androida ani
konta Expo. Wymaga to Ciebie, jednorazowo:

```sh
npm install --global eas-cli
cd mobile
eas login              # załóż darmowe konto na expo.dev, jeśli nie masz
eas build:configure    # wybierz Android
eas build --platform android --profile preview
```

EAS Build jest darmowy (limit buildów/miesiąc w darmowym planie, więcej niż
wystarczy na testy). Build trwa zwykle kilka-kilkanaście minut w chmurze
Expo, na koniec dostajesz link do pobrania `.apk` — instalujesz go na
telefonie kierowcy bezpośrednio (nie trzeba Google Play, chyba że
zechcecie tam kiedyś publikować — to osobny, płatny jednorazowo $25
rejestracja Google Play Developer).

Przy pierwszym buildzie EAS zapyta o wygenerowanie klucza podpisującego
Androida — wybierz "Generate new keystore" (EAS przechowa go za Ciebie,
potrzebny do każdego kolejnego builda tej samej appki).

## Zmienne środowiskowe

`EXPO_PUBLIC_API_BASE_URL` — adres backendu (domyślnie produkcja,
`https://api.dowieziemycie.pl`). Prefiks `EXPO_PUBLIC_` jest wymagany przez
Expo, żeby zmienna trafiła do zbudowanej aplikacji.

## Struktura

```
app/                    — ekrany (Expo Router, routing plikowy)
  _layout.tsx            — root layout, rejestruje zadanie w tle
  index.tsx               — przekierowanie wg stanu logowania
  login.tsx
  (app)/
    _layout.tsx            — zakładki (chronione, wymaga logowania)
    dashboard.tsx           — status + wskaźnik śledzenia
    bookings.tsx            — nowe kursy do przyjęcia
    schedule.tsx            — harmonogram dnia
src/lib/
  api.ts                  — klient HTTP
  session.ts               — bezpieczny magazyn JWT (expo-secure-store)
  auth-context.tsx          — stan logowania (React Context)
  location-task.ts          — zadanie GPS w tle
  notifications.ts          — rejestracja push
  theme.ts                  — kolory (spójne ze stroną WWW)
```
