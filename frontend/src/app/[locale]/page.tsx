import { setRequestLocale } from "next-intl/server";

import { AboutSection } from "@/components/about-section";
import { FleetSection } from "@/components/fleet-section";
import { HeroSection } from "@/components/hero-section";
import { HowItWorksSection } from "@/components/how-it-works-section";
import { LocalRoutesSection } from "@/components/local-routes-section";
import { PricingTierSection } from "@/components/pricing-tier-section";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { StatusLegendSection } from "@/components/status-legend-section";

export default async function Home({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <SiteHeader />
      <main>
        <HeroSection />
        <StatusLegendSection />
        <PricingTierSection />
        <HowItWorksSection />
        <LocalRoutesSection />
        <FleetSection />
        <AboutSection />
      </main>
      <SiteFooter />
    </>
  );
}
