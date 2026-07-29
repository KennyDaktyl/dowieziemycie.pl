import { setRequestLocale } from "next-intl/server";

import { DriverLoginForm } from "@/components/driver-login-form";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default async function DriverLoginPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <SiteHeader />
      <main className="px-6 py-16">
        <DriverLoginForm />
      </main>
      <SiteFooter />
    </>
  );
}
