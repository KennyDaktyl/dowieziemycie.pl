"use client";

import {
  Elements,
  ExpressCheckoutElement,
  PaymentElement,
  useElements,
  useStripe,
} from "@stripe/react-stripe-js";
import { loadStripe, type Stripe } from "@stripe/stripe-js";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useRef, useState } from "react";

import { PaymentBadge } from "@/components/payment-badge";
import { netFromGross } from "@/lib/format";

type Phase = "idle" | "loading" | "form" | "processing";
export type PaymentKind = "deposit" | "full" | "remainder";

function Spinner({ className = "text-amber" }: { className?: string }) {
  return (
    <svg className={`h-4 w-4 shrink-0 animate-spin ${className}`} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

const LABEL_KEYS: Record<PaymentKind, "payDeposit" | "payFull" | "payRemainder"> = {
  deposit: "payDeposit",
  full: "payFull",
  remainder: "payRemainder",
};

export function DepositPaymentForm({
  bookingId,
  amount,
  kind = "deposit",
  showVatNote = true,
}: {
  bookingId: number;
  amount: string;
  kind?: PaymentKind;
  showVatNote?: boolean;
}) {
  const t = useTranslations("BookingPayment");
  const [phase, setPhase] = useState<Phase>("idle");
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stripePromiseRef = useRef<Promise<Stripe | null> | null>(null);

  async function startPayment() {
    setPhase("loading");
    setError(null);
    try {
      const res = await fetch(`/api/bookings/${bookingId}/create-payment-intent`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ kind }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail ?? t("error"));
        setPhase("idle");
        return;
      }
      stripePromiseRef.current = loadStripe(data.publishable_key);
      setClientSecret(data.client_secret);
      setPhase("form");
    } catch {
      setError(t("error"));
      setPhase("idle");
    }
  }

  if (phase === "processing") {
    return (
      <div className="flex w-full items-center gap-2.5 rounded-[9px] bg-panel-2 px-5 py-2.5 text-[13px] font-semibold text-muted">
        <Spinner />
        {t("processing")}
      </div>
    );
  }

  if (phase === "form" && clientSecret && stripePromiseRef.current) {
    return (
      <div className="w-full min-w-0">
        <Elements stripe={stripePromiseRef.current} options={{ clientSecret }}>
          <PaymentElementForm
            bookingId={bookingId}
            amount={amount}
            kind={kind}
            onProcessing={() => setPhase("processing")}
            onError={(msg) => setError(msg)}
          />
        </Elements>
        {error && <span className="mt-3 block text-[12px] text-red">{error}</span>}
      </div>
    );
  }

  const net = netFromGross(amount);

  return (
    <div className="flex w-full min-w-[220px] flex-col items-start gap-2 sm:w-auto">
      <PaymentBadge label={t("securePayments")} sublabel={t("paymentMethods")} />
      <button
        type="button"
        onClick={startPayment}
        disabled={phase === "loading"}
        className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-[9px] bg-amber px-5 py-2.5 text-[14px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:shadow-none sm:w-auto"
      >
        {phase === "loading" && <Spinner className="text-[#1a1305]" />}
        {phase === "loading" ? t("paying") : t(LABEL_KEYS[kind], { amount: Number(amount).toFixed(0) })}
      </button>
      {showVatNote && <span className="text-[12px] text-muted">{t("vatNote", { net: net.toFixed(2) })}</span>}
      {error && <span className="text-[12px] text-red">{error}</span>}
    </div>
  );
}

function PaymentElementForm({
  bookingId,
  amount,
  kind,
  onProcessing,
  onError,
}: {
  bookingId: number;
  amount: string;
  kind: PaymentKind;
  onProcessing: () => void;
  onError: (message: string) => void;
}) {
  const t = useTranslations("BookingPayment");
  const stripe = useStripe();
  const elements = useElements();
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);

  async function confirm() {
    if (!stripe || !elements) return;
    setSubmitting(true);
    onError("");

    const { error } = await stripe.confirmPayment({
      elements,
      redirect: "if_required",
      confirmParams: { return_url: window.location.href },
    });

    if (error) {
      onError(error.message ?? t("error"));
      setSubmitting(false);
      return;
    }

    onProcessing();
    await pollUntilPaid(bookingId, kind, router);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await confirm();
  }

  // Renders nothing when the customer's browser/device has no wallet
  // available (no Apple Pay set up, not Safari/Chrome, etc.) — Stripe
  // decides that automatically, nothing to gate here.
  async function handleExpressConfirm() {
    if (!stripe || !elements) return;
    const { error: submitError } = await elements.submit();
    if (submitError) {
      onError(submitError.message ?? t("error"));
      return;
    }
    await confirm();
  }

  return (
    <form onSubmit={handleSubmit} className="flex w-full min-w-0 flex-col gap-3">
      <div className="w-full [&_.StripeElement]:w-full">
        <ExpressCheckoutElement
          onConfirm={handleExpressConfirm}
          options={{
            // By default Stripe only shows a wallet button if it detects a
            // saved card for it already — on a browser/OS with no card saved
            // to Google Pay, the button just silently doesn't render at all,
            // which reads as "Apple Pay/Google Pay isn't working" when it's
            // actually working as designed. "always" shows the button
            // regardless and lets the customer add a card inside the wallet
            // popup itself. Apple Pay still only ever appears in Safari on
            // Apple hardware — that's an OS-level restriction, not something
            // any of these options can change.
            // Link (Stripe's own one-click checkout) is unfamiliar to most
            // customers here and was showing up as an express button
            // alongside the wallets — explicitly excluded regardless of the
            // account-level default.
            paymentMethods: { applePay: "always", googlePay: "always", link: "never" },
          }}
        />
      </div>
      <PaymentElement />
      <button
        type="submit"
        disabled={!stripe || submitting}
        className="flex w-full cursor-pointer items-center justify-center gap-2 rounded-[9px] bg-amber px-5 py-2.5 text-[14px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:shadow-none"
      >
        {submitting && <Spinner className="text-[#1a1305]" />}
        {submitting ? t("paying") : t(LABEL_KEYS[kind], { amount: Number(amount).toFixed(0) })}
      </button>
    </form>
  );
}

/** The webhook (not the client-side confirmPayment result) is the source of
 * truth for "did the money actually land" — BLIK in particular can take up
 * to ~2 minutes for the customer to confirm in their banking app, so we
 * poll the booking's own state rather than trusting confirmPayment's
 * immediate return value. A deposit payment is "done" once the booking
 * reaches OPLACONA; a full or remainder payment settles the balance
 * without necessarily changing status, so those wait for
 * remainder_paid_at instead. */
async function pollUntilPaid(bookingId: number, kind: PaymentKind, router: ReturnType<typeof useRouter>) {
  for (let attempt = 0; attempt < 24; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
    const res = await fetch("/api/bookings/mine", { cache: "no-store" });
    if (res.ok) {
      const bookings: { id: number; status: string; remainder_paid_at: string | null }[] = await res.json();
      const booking = bookings.find((b) => b.id === bookingId);
      if (!booking) continue;
      const done = kind === "deposit" ? booking.status === "OPLACONA" : booking.remainder_paid_at != null;
      if (done) {
        router.refresh();
        return;
      }
    }
  }
  router.refresh();
}
