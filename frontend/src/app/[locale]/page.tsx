import { setRequestLocale } from "next-intl/server";

import { AboutSection } from "@/components/about-section";
import { FleetSection } from "@/components/fleet-section";
import { HeroSection } from "@/components/hero-section";
import { HowItWorksSection } from "@/components/how-it-works-section";
import { LocalRoutesSection } from "@/components/local-routes-section";
import { OrganizationJsonLd } from "@/components/organization-jsonld";
import { PillarsSection } from "@/components/pillars-section";
import { PricingTierSection } from "@/components/pricing-tier-section";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { StatusLegendSection } from "@/components/status-legend-section";
import { TopicTilesSection } from "@/components/topic-tiles-section";

export default async function Home({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <OrganizationJsonLd />
      <SiteHeader />
      <main>
        <HeroSection />
        <FleetSection />
        <PillarsSection />
        <TopicTilesSection />
        <StatusLegendSection />
        <PricingTierSection />
        <HowItWorksSection />
        <LocalRoutesSection />
        <AboutSection />
      </main>
      <SiteFooter />
    </>
  );
}
