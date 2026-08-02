const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

export function OrganizationJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": "TaxiService",
    name: "dowieziemycie.pl",
    url: SITE_URL,
    logo: `${SITE_URL}/pl/icon`,
    image: `${SITE_URL}/pl/opengraph-image`,
    telephone: "+48506029980",
    email: "kontakt@dowieziemycie.pl",
    areaServed: {
      "@type": "City",
      name: "Kraków",
    },
    priceRange: "PLN",
  };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
