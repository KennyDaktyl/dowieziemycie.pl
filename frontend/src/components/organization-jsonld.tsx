import { apiFetch } from "@/lib/api";
import type { ContactInfo } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";

export async function OrganizationJsonLd() {
  const contact = await apiFetch<ContactInfo>("/api/contact-info/", { next: { revalidate: 60 } });
  const data = {
    "@context": "https://schema.org",
    "@type": "TaxiService",
    name: "dowieziemycie.pl",
    legalName: contact.legal_name,
    url: SITE_URL,
    logo: `${SITE_URL}/pl/icon`,
    image: `${SITE_URL}/pl/opengraph-image`,
    telephone: contact.phone,
    email: contact.email,
    taxID: contact.nip,
    address: {
      "@type": "PostalAddress",
      streetAddress: contact.address_street,
      postalCode: contact.address_postal_code,
      addressLocality: contact.address_city,
      addressCountry: contact.address_country,
    },
    areaServed: {
      "@type": "City",
      name: "Kraków",
    },
    priceRange: "PLN",
  };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
