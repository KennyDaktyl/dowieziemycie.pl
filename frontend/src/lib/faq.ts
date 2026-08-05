export type FaqPair = { question: string; answer: string };

/** Pulls Q&A pairs out of CMS Markdown body text for FAQPage JSON-LD,
 * instead of adding a separate structured FAQ field to every content
 * model. FAQ sections in this CMS are already written as
 * "**Question?**\nAnswer." blocks — scoped to whatever comes after the
 * "## FAQ" / "## Najczęściej zadawane pytania" heading so a bolded first
 * line elsewhere in the article is never mistaken for a question. */
export function extractFaqPairs(markdown: string): FaqPair[] {
  if (!markdown) return [];
  const headingMatch = markdown.match(
    /^##\s*(FAQ|Najczęściej zadawane pytania|Frequently Asked Questions)\s*$/im,
  );
  const section = headingMatch ? markdown.slice(headingMatch.index! + headingMatch[0].length) : markdown;

  const pairs: FaqPair[] = [];
  for (const block of section.split(/\n\s*\n+/)) {
    const match = block.trim().match(/^\*\*(.+?)\*\*\n([\s\S]+)$/);
    if (match) {
      pairs.push({ question: match[1].trim(), answer: match[2].trim().replace(/\s+/g, " ") });
    }
  }
  return pairs;
}
