import { setRequestLocale } from "next-intl/server";

import { DriverPanel } from "@/components/driver-panel";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default async function DriverPanelPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <SiteHeader />
      <main className="px-6 py-16">
        <DriverPanel />
      </main>
      <SiteFooter />
    </>
  );
}
