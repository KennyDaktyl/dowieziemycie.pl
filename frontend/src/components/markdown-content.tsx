import { marked } from "marked";

marked.setOptions({ breaks: true });

/** Renders admin-authored CMS markdown as HTML. Content comes from Django
 * Admin, not user input — same trust level as everything else pulled from
 * the CMS, so no sanitizer pass is needed. */
export function MarkdownContent({ markdown, className = "" }: { markdown: string; className?: string }) {
  if (!markdown.trim()) return null;
  const html = marked.parse(markdown, { async: false });
  return <div className={`prose-content ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}
