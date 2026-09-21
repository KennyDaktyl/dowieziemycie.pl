import { NextRequest, NextResponse } from "next/server";

import { apiBaseUrl, withSiteHeader } from "@/lib/api";

/**
 * Short payment link from the deposit / balance SMS: /pay/<token>.
 *
 * Asks the backend what the booking owes right now and 302s to the matching
 * Stripe Checkout page. The Checkout URL itself is 400+ characters — useless
 * in an SMS — so the SMS carries this short, brand-domain link instead. Lives
 * outside [locale] on purpose (the customer's language comes from the
 * booking, not from the URL) and is excluded from the locale proxy.
 */

type Lang = "pl" | "en" | "de";

type Message = { title: string; text: string };

const MESSAGES: Record<Lang, { home: string; messages: Record<string, Message> }> = {
  pl: {
    home: "Wróć na stronę główną",
    messages: {
      expired: {
        title: "Link do płatności wygasł",
        text: "Czas na zapłatę zaliczki minął, a rezerwacja wygasła. Zarezerwuj kurs ponownie lub skontaktuj się z nami.",
      },
      already_paid: { title: "Ten kurs jest już opłacony", text: "Nic więcej nie musisz płacić. Dziękujemy!" },
      unavailable: {
        title: "Link do płatności jest nieaktualny",
        text: "Ta rezerwacja nie oczekuje na płatność (mogła zostać anulowana). Skontaktuj się z nami, jeśli to pomyłka.",
      },
      error: { title: "Nie udało się utworzyć płatności", text: "Spróbuj ponownie za chwilę." },
    },
  },
  en: {
    home: "Back to the homepage",
    messages: {
      expired: {
        title: "This payment link has expired",
        text: "The time to pay the deposit has passed and the booking has expired. Please book again or contact us.",
      },
      already_paid: { title: "This ride is already paid for", text: "There is nothing more to pay. Thank you!" },
      unavailable: {
        title: "This payment link is no longer valid",
        text: "This booking is not waiting for a payment (it may have been cancelled). Contact us if this is a mistake.",
      },
      error: { title: "We couldn't start the payment", text: "Please try again in a moment." },
    },
  },
  de: {
    home: "Zur Startseite",
    messages: {
      expired: {
        title: "Dieser Zahlungslink ist abgelaufen",
        text: "Die Frist für die Anzahlung ist abgelaufen und die Buchung verfallen. Bitte buchen Sie erneut oder kontaktieren Sie uns.",
      },
      already_paid: { title: "Diese Fahrt ist bereits bezahlt", text: "Sie müssen nichts weiter zahlen. Vielen Dank!" },
      unavailable: {
        title: "Dieser Zahlungslink ist nicht mehr gültig",
        text: "Diese Buchung erwartet keine Zahlung (sie wurde eventuell storniert). Kontaktieren Sie uns, falls das ein Irrtum ist.",
      },
      error: { title: "Die Zahlung konnte nicht gestartet werden", text: "Bitte versuchen Sie es gleich noch einmal." },
    },
  },
};

const HEADERS = { "X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store" };

function messagePage(language: string, code: string): NextResponse {
  const lang: Lang = language === "en" || language === "de" ? language : "pl";
  const dict = MESSAGES[lang];
  const { title, text } = dict.messages[code] ?? dict.messages.error;
  const html = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>${title}</title></head>
<body style="font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;padding:48px 20px;background:#f6f6f7;color:#1d1d1f">
<main style="max-width:460px;margin:0 auto;background:#fff;border-radius:14px;padding:28px 24px;box-shadow:0 1px 4px rgba(0,0,0,.08)">
<h1 style="font-size:20px;margin:0 0 12px">${title}</h1>
<p style="font-size:15px;line-height:1.55;margin:0 0 20px">${text}</p>
<a href="/${lang}" style="color:#0a58ca">${dict.home}</a></main></body></html>`;
  return new NextResponse(html, {
    status: 200,
    headers: { ...HEADERS, "Content-Type": "text/html; charset=utf-8" },
  });
}

export async function GET(_request: NextRequest, { params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  let res: Response;
  try {
    res = await fetch(`${apiBaseUrl()}/api/pay/${encodeURIComponent(token)}/`, {
      headers: withSiteHeader(),
      cache: "no-store",
    });
  } catch {
    return messagePage("pl", "error");
  }
  const data = await res.json().catch(() => ({}));
  if (res.ok && typeof data.url === "string") {
    return NextResponse.redirect(data.url, { status: 302, headers: HEADERS });
  }
  return messagePage(data.language ?? "pl", data.code ?? "error");
}
