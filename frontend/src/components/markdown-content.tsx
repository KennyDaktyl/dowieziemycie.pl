import { marked } from "marked";

import type { AppLocale } from "@/i18n/routing";
import { routing } from "@/i18n/routing";

marked.setOptions({ breaks: true });

const LOCALE_PREFIX_RE = new RegExp(`^/(?:${routing.locales.join("|")})(?:/|$)`);

/** CMS bodies (Markdown, authored once per locale in Django Admin) link to
 * other pages with site-relative paths, e.g. "/trasa/krakow-balice" —
 * without a locale prefix, since the author doesn't know which locale will
 * render the link. Left as-is, that renders as a literal unprefixed
 * <a href>, which next-intl's middleware then redirects to the current
 * locale — wasted crawl budget and exactly the kind of "page contains a
 * redirect" internal link GSC's coverage report flags (same bug and same
 * fix as transfer247.pl's MarkdownContent, see that repo's commit
 * d45f46e — this component just never got the same fix since it's a
 * separate file in a separate repo). Skips image markdown
 * (`![alt](/path)`) and anything already locale-prefixed, anchors,
 * mailto:/tel:/http(s):. */
function localizeMarkdownLinks(markdown: string, locale: AppLocale): string {
  return markdown.replace(/(!?)(\]\()(\/[^)\s]*)/g, (match, bang: string, open: string, path: string) => {
    if (bang || LOCALE_PREFIX_RE.test(path)) return match;
    // A bare root-relative anchor ("/#fleet", linking to a homepage section)
    // would otherwise become "/pl/#fleet" — the leading "/" is the anchor's,
    // not a path segment, so drop it before appending to the locale prefix.
    if (path.startsWith("/#")) return `${bang}${open}/${locale}${path.slice(1)}`;
    return `${bang}${open}/${locale}${path}`;
  });
}

/** Renders admin-authored CMS markdown as HTML. Content comes from Django
 * Admin, not user input — same trust level as everything else pulled from
 * the CMS, so no sanitizer pass is needed. Pass `locale` whenever the
 * markdown may contain internal links, so they get rewritten to the
 * current locale (see `localizeMarkdownLinks`). */
export function MarkdownContent({
  markdown,
  locale,
  className = "",
}: {
  markdown: string;
  locale?: AppLocale;
  className?: string;
}) {
  if (!markdown.trim()) return null;
  const source = locale ? localizeMarkdownLinks(markdown, locale) : markdown;
  const html = marked.parse(source, { async: false });
  return <div className={`prose-content ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}
