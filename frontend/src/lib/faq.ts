export type FaqPair = { question: string; answer: string };

const FAQ_HEADING_RE = /^##\s*(FAQ|Najczęściej zadawane pytania|Frequently Asked Questions)\s*$/im;
const QA_BLOCK_RE = /^\*\*(.+?)\*\*\n([\s\S]+)$/;

/** FAQPage's Answer.text must be the plain text a user would read — not
 * Markdown source. Answers that link elsewhere ("see [the guide](/blog/…)")
 * would otherwise leak "[label](url)" into the JSON-LD. */
function toPlainText(markdown: string): string {
  return markdown
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

/** Pulls Q&A pairs out of CMS Markdown body text for FAQPage JSON-LD,
 * instead of adding a separate structured FAQ field to every content
 * model. FAQ sections in this CMS are already written as
 * "**Question?**\nAnswer." blocks — scoped to whatever comes after the
 * "## FAQ" / "## Najczęściej zadawane pytania" heading so a bolded first
 * line elsewhere in the article is never mistaken for a question. */
export function extractFaqPairs(markdown: string): FaqPair[] {
  if (!markdown) return [];
  const headingMatch = markdown.match(FAQ_HEADING_RE);
  const section = headingMatch ? markdown.slice(headingMatch.index! + headingMatch[0].length) : markdown;

  const pairs: FaqPair[] = [];
  for (const block of section.replace(/\r\n/g, "\n").split(/\n\s*\n+/)) {
    const match = block.trim().match(QA_BLOCK_RE);
    if (match) {
      pairs.push({ question: toPlainText(match[1]), answer: toPlainText(match[2]) });
    }
  }
  return pairs;
}

/** Splits a body into what comes before its FAQ section, the FAQ heading,
 * the Q&A pairs (answers kept as Markdown, links intact) and whatever
 * follows them — so a page can render the FAQ as <details> accordions
 * (no JS) while the rest stays ordinary Markdown. No FAQ heading: the whole
 * body is `before`. */
export function splitFaqSection(markdown: string): {
  before: string;
  heading: string;
  pairs: { question: string; answerMarkdown: string }[];
  after: string;
} {
  const body = (markdown ?? "").replace(/\r\n/g, "\n");
  const headingMatch = body.match(FAQ_HEADING_RE);
  if (!headingMatch) return { before: body, heading: "", pairs: [], after: "" };

  const before = body.slice(0, headingMatch.index!);
  const heading = headingMatch[1];
  const rest = body.slice(headingMatch.index! + headingMatch[0].length);
  const pairs: { question: string; answerMarkdown: string }[] = [];
  const after: string[] = [];
  for (const block of rest.split(/\n\s*\n+/)) {
    const trimmed = block.trim();
    if (!trimmed) continue;
    const match = trimmed.match(QA_BLOCK_RE);
    // A non-Q&A block after the first question ends the FAQ list.
    if (match && after.length === 0) pairs.push({ question: match[1].trim(), answerMarkdown: match[2].trim() });
    else after.push(trimmed);
  }
  return { before, heading, pairs, after: after.join("\n\n") };
}
