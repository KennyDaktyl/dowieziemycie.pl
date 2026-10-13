import { apiFetch } from "@/lib/api";
import type { ContactInfo } from "@/lib/types";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dowieziemycie.pl";
const AREA_SERVED = [
  "Rybna",
  "Czernichów",
  "Liszki",
  "Kaszów",
  "Sanka",
  "Alwernia",
  "Przeginia Narodowa",
  "Kraków",
];

export async function OrganizationJsonLd() {
  const contact = await apiFetch<ContactInfo>("/api/contact-info/");
  const data = {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    serviceType: "Przewóz osób busem z kierowcą",
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
    areaServed: AREA_SERVED.map((place) => ({ "@type": "Place", name: place })),
    priceRange: "PLN",
  };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
