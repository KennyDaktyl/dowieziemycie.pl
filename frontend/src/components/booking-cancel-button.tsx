"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function BookingCancelButton({ bookingId }: { bookingId: number }) {
  const t = useTranslations("BookingPayment");
  const router = useRouter();
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleCancel() {
    if (!window.confirm(t("cancelConfirm"))) return;
    setCancelling(true);
    setError(null);
    try {
      const res = await fetch(`/api/bookings/${bookingId}/cancel`, { method: "POST" });
      if (!res.ok) throw new Error();
      router.refresh();
    } catch {
      setError(t("cancelError"));
    } finally {
      setCancelling(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <button
        type="button"
        onClick={handleCancel}
        disabled={cancelling}
        className="cursor-pointer text-[12.5px] font-semibold text-muted underline decoration-muted/50 underline-offset-2 transition-colors hover:text-red disabled:cursor-not-allowed disabled:opacity-60"
      >
        {cancelling ? t("cancelling") : t("cancel")}
      </button>
      {error && <span className="text-[11.5px] text-red">{error}</span>}
    </div>
  );
}
