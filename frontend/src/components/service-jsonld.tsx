import { siteUrl } from "@/lib/seo";
import type { ServicePricingOption } from "@/lib/types";

const AREA_SERVED = [
  "Kraków", "Rybna", "Liszki", "Kaszów", "Czernichów", "Sanka", "Przeginia Narodowa", "Alwernia", "Krzeszowice",
];

/** Service for a service page ("Transport rzeczy" and its subpages), with
 * an Offer per pricing option that has a real price — options "on request"
 * or still without a price add none rather than a made-up one. */
export function ServiceJsonLd({
  name,
  description,
  path,
  phone,
  image,
  options,
}: {
  name: string;
  description: string;
  path: string;
  phone: string;
  image?: string;
  options: ServicePricingOption[];
}) {
  const url = `${siteUrl()}${path}`;
  const offers = options
    .filter((option) => option.price_from && !option.on_request)
    .map((option) => ({
      "@type": "Offer",
      name: option.name_pl,
      url,
      priceCurrency: "PLN",
      priceSpecification: {
        "@type": "PriceSpecification",
        minPrice: Number(option.price_from),
        priceCurrency: "PLN",
        valueAddedTaxIncluded: true,
      },
    }));
  const data = {
    "@context": "https://schema.org",
    "@type": "Service",
    serviceType: "Transport mebli i rzeczy",
    name,
    description,
    url,
    ...(image ? { image } : {}),
    provider: { "@type": "LocalBusiness", name: "dowieziemycie.pl", url: siteUrl(), telephone: phone },
    areaServed: AREA_SERVED.map((place) => ({ "@type": "Place", name: place })),
    ...(offers.length ? { offers } : {}),
  };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
