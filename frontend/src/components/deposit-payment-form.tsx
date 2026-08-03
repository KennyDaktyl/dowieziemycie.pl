"use client";

import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import { loadStripe, type Stripe } from "@stripe/stripe-js";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useRef, useState } from "react";

import { PaymentBadge } from "@/components/payment-badge";
import { netFromGross } from "@/lib/format";

type Phase = "idle" | "loading" | "form" | "processing";

export function DepositPaymentForm({ bookingId, depositAmount }: { bookingId: number; depositAmount: string }) {
  const t = useTranslations("BookingPayment");
  const [phase, setPhase] = useState<Phase>("idle");
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stripePromiseRef = useRef<Promise<Stripe | null> | null>(null);

  async function startPayment() {
    setPhase("loading");
    setError(null);
    try {
      const res = await fetch(`/api/bookings/${bookingId}/create-payment-intent`, { method: "POST" });
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
    return <p className="text-[13px] text-muted">{t("processing")}</p>;
  }

  if (phase === "form" && clientSecret && stripePromiseRef.current) {
    return (
      <div className="flex flex-col gap-3">
        <Elements stripe={stripePromiseRef.current} options={{ clientSecret }}>
          <PaymentElementForm
            bookingId={bookingId}
            amount={depositAmount}
            onProcessing={() => setPhase("processing")}
            onError={(msg) => setError(msg)}
          />
        </Elements>
        {error && <span className="text-[12px] text-red">{error}</span>}
      </div>
    );
  }

  const net = netFromGross(depositAmount);

  return (
    <div className="flex flex-col items-start gap-2">
      <PaymentBadge label={t("securePayments")} sublabel={t("paymentMethods")} />
      <button
        type="button"
        onClick={startPayment}
        disabled={phase === "loading"}
        className="rounded-[9px] bg-amber px-5 py-2.5 text-[14px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:opacity-60"
      >
        {phase === "loading" ? t("paying") : t("payDeposit", { amount: Number(depositAmount).toFixed(0) })}
      </button>
      <span className="text-[12px] text-muted">{t("vatNote", { net: net.toFixed(2) })}</span>
      {error && <span className="text-[12px] text-red">{error}</span>}
    </div>
  );
}

function PaymentElementForm({
  bookingId,
  amount,
  onProcessing,
  onError,
}: {
  bookingId: number;
  amount: string;
  onProcessing: () => void;
  onError: (message: string) => void;
}) {
  const t = useTranslations("BookingPayment");
  const stripe = useStripe();
  const elements = useElements();
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
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
    await pollUntilPaid(bookingId, router);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <PaymentElement />
      <button
        type="submit"
        disabled={!stripe || submitting}
        className="rounded-[9px] bg-amber px-5 py-2.5 text-[14px] font-bold text-[#1a1305] transition-all hover:-translate-y-px hover:shadow-[0_6px_22px_rgba(245,166,35,0.3)] disabled:opacity-60"
      >
        {submitting ? t("paying") : t("payDeposit", { amount: Number(amount).toFixed(0) })}
      </button>
    </form>
  );
}

/** The webhook (not the client-side confirmPayment result) is the source of
 * truth for "did the deposit actually land" — BLIK in particular can take
 * up to ~2 minutes for the customer to confirm in their banking app, so we
 * poll the booking's own status rather than trusting confirmPayment's
 * immediate return value. */
async function pollUntilPaid(bookingId: number, router: ReturnType<typeof useRouter>) {
  for (let attempt = 0; attempt < 24; attempt += 1) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
    const res = await fetch("/api/bookings/mine", { cache: "no-store" });
    if (res.ok) {
      const bookings: { id: number; status: string }[] = await res.json();
      const booking = bookings.find((b) => b.id === bookingId);
      if (booking?.status === "OPLACONA") {
        router.refresh();
        return;
      }
    }
  }
  router.refresh();
}
