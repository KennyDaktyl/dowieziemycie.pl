const XSL = `<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
  xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <xsl:output method="html" encoding="UTF-8" indent="yes" />
  <xsl:template match="/">
    <html lang="pl">
      <head>
        <title>Sitemap - dowieziemycie.pl</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
          body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #111827; background: #f9fafb; }
          h1 { margin: 0 0 8px; font-size: 28px; }
          p { margin: 0 0 24px; color: #4b5563; }
          table { width: 100%; border-collapse: collapse; background: white; border: 1px solid #e5e7eb; }
          th, td { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; vertical-align: top; font-size: 14px; }
          th { background: #f3f4f6; font-weight: 700; }
          a { color: #b45309; text-decoration: none; }
          a:hover { text-decoration: underline; }
          code { color: #374151; }
        </style>
      </head>
      <body>
        <h1>Sitemap - dowieziemycie.pl</h1>
        <p>
          <xsl:value-of select="count(sitemap:urlset/sitemap:url)" />
          <xsl:text> adresów URL w mapie witryny.</xsl:text>
        </p>
        <table>
          <thead>
            <tr>
              <th>URL</th>
              <th>Zmiany</th>
              <th>Priorytet</th>
              <th>Wersje językowe</th>
            </tr>
          </thead>
          <tbody>
            <xsl:for-each select="sitemap:urlset/sitemap:url">
              <tr>
                <td><a href="{sitemap:loc}"><xsl:value-of select="sitemap:loc" /></a></td>
                <td><code><xsl:value-of select="sitemap:changefreq" /></code></td>
                <td><code><xsl:value-of select="sitemap:priority" /></code></td>
                <td>
                  <xsl:for-each select="xhtml:link">
                    <div>
                      <code><xsl:value-of select="@hreflang" /></code>
                      <xsl:text>: </xsl:text>
                      <a href="{@href}"><xsl:value-of select="@href" /></a>
                    </div>
                  </xsl:for-each>
                </td>
              </tr>
            </xsl:for-each>
          </tbody>
        </table>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
`;

export const dynamic = "force-static";

export async function GET() {
  return new Response(XSL, {
    headers: {
      "Cache-Control": "public, max-age=86400",
      "Content-Type": "application/xslt+xml; charset=utf-8",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
