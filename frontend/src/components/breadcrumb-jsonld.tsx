import { siteUrl } from "@/lib/seo";

/** Structured twin of the visual <Breadcrumbs> component — pass the same
 * items array to both. `href` entries are resolved to absolute URLs;
 * the final (current-page) item is expected to have no href, matching how
 * <Breadcrumbs> already renders it as plain text. */
export function BreadcrumbJsonLd({
  items,
  locale,
}: {
  items: { label: string; href?: string }[];
  locale: string;
}) {
  const data = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.label,
      ...(item.href ? { item: `${siteUrl()}/${locale}${item.href}` } : {}),
    })),
  };

  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />;
}
