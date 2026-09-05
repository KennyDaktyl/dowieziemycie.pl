import { getTranslations } from "next-intl/server";

import { ObfuscatedEmail } from "@/components/obfuscated-email";
import { PaymentBadge } from "@/components/payment-badge";
import { Link } from "@/i18n/navigation";
import { apiBaseUrl, apiFetch } from "@/lib/api";
import type { ContactInfo } from "@/lib/types";

export async function SiteFooter() {
  const [t, tPayment, contact] = await Promise.all([
    getTranslations("Footer"),
    getTranslations("BookingPayment"),
    apiFetch<ContactInfo>("/api/contact-info/", { next: { revalidate: 60 } }),
  ]);
  const [emailUser, emailDomain] = contact.email.split("@");
  const address = `${contact.address_street}, ${contact.address_postal_code} ${contact.address_city}`;

  return (
    <footer className="border-t border-line px-6 pt-11 pb-[30px]">
      <div className="mx-auto max-w-[1360px]">
        <div className="flex flex-wrap justify-between gap-6">
          <div>
            <Link href="/" className="font-heading mb-2.5 flex items-center gap-2 text-[19px] font-bold">
              <span className="h-[9px] w-[9px] rounded-full bg-amber shadow-[0_0_12px_2px_var(--color-amber)]" />
              dowieziemycie<span className="text-amber">.pl</span>
            </Link>
            <p className="text-[13.5px] leading-[1.7] text-muted">
              {t("tagline")}
              <br />
              {t("tagline2")}
            </p>
          </div>
          <div>
            <p className="text-[13.5px] leading-[1.7] text-muted">
              <a href={`tel:${contact.phone}`}>{contact.phone_display}</a>
              <br />
              <ObfuscatedEmail user={emailUser} domain={emailDomain} />
            </p>
            <Link href="/regulamin" className="mt-2.5 inline-block text-[13.5px] text-muted hover:text-text">
              {t("terms")}
            </Link>
          </div>
          <PaymentBadge label={tPayment("securePayments")} sublabel={tPayment("paymentMethods")} />
        </div>
        <div className="mt-[30px] flex flex-wrap justify-between gap-2.5 border-t border-line pt-5 text-[12.5px] text-muted">
          <span>
            {contact.legal_name} · NIP {contact.nip} · {address} ·{" "}
            {t("rights", { year: new Date().getFullYear() })}
          </span>
          <a href={`${apiBaseUrl()}/admin/`} className="opacity-60 transition-opacity hover:opacity-100">
            {t("adminPanel")}
          </a>
        </div>
      </div>
    </footer>
  );
}
