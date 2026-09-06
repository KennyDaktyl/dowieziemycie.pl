import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";
import { notFound } from "next/navigation";

import { Breadcrumbs } from "@/components/breadcrumbs";
import { MarkdownContent } from "@/components/markdown-content";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { BlogPost } from "@/lib/types";

async function getPosts(): Promise<BlogPost[]> {
  return apiFetch<BlogPost[]>("/api/blog/", { next: { revalidate: 60 } }).catch(() => []);
}

async function getPost(slug: string): Promise<BlogPost | null> {
  return apiFetch<BlogPost>(`/api/blog/${slug}/`, { next: { revalidate: 60 } }).catch(() => null);
}

export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string; slug: string }>;
}): Promise<Metadata> {
  const { locale, slug } = await params;
  const post = await getPost(slug);
  if (!post) return {};
  const appLocale = locale as AppLocale;
  const title = localize(post, "seo_title", appLocale) || localize(post, "title", appLocale);
  const description = localize(post, "seo_description", appLocale) || localize(post, "excerpt", appLocale);
  return { title, description, alternates: buildAlternates(`/blog/${slug}`, appLocale) };
}

export default async function BlogPostPage({ params }: { params: Promise<{ locale: string; slug: string }> }) {
  const { locale, slug } = await params;
  setRequestLocale(locale);

  const [t, tCrumbs, appLocale, post] = await Promise.all([
    getTranslations("Blog"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    getPost(slug),
  ]);

  if (!post) notFound();

  const tag = localize(post, "tag", appLocale);
  const title = localize(post, "title", appLocale);
  const body = localize(post, "body", appLocale) || localize(post, "excerpt", appLocale);
  const sortedLinks = [...post.links].sort((a, b) => a.order - b.order);

  return (
    <>
      <SiteHeader />
      <main>
        <div className="mx-auto max-w-[1360px] px-4 py-14 sm:px-6 sm:py-20">
          <Breadcrumbs
            items={[{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("blog"), href: "/blog" }, { label: title }]}
          />

          <Link href="/blog" className="mt-3 inline-block text-[13px] font-medium text-amber">
            {t("backToIndex")}
          </Link>

          <div className="mt-4 flex items-center gap-3 text-[13px] text-muted">
            {tag ? <span className="font-medium text-amber">{tag}</span> : null}
            <time dateTime={post.published_at}>{post.published_at}</time>
          </div>
          <h1 className="font-heading mt-2 text-[30px] leading-[1.15] font-semibold text-text sm:text-[42px]">
            {title}
          </h1>

          {post.cover_image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={absoluteImageUrl(post.cover_image)}
              alt={title}
              className="mt-8 h-[240px] w-full rounded-[14px] object-cover sm:h-[380px]"
            />
          ) : null}

          <div className="mt-8 grid grid-cols-1 gap-10 lg:grid-cols-[1fr_280px]">
            <MarkdownContent markdown={body} />

            {sortedLinks.length > 0 ? (
              <aside className="h-fit rounded-[14px] border border-line bg-panel p-5">
                <h2 className="font-label text-xs font-semibold tracking-[0.1em] text-muted uppercase">
                  {t("usefulLinksHeading")}
                </h2>
                <ul className="mt-3 flex flex-col gap-2.5">
                  {sortedLinks.map((link) =>
                    link.url.startsWith("/") ? (
                      <li key={link.url}>
                        <Link
                          href={link.url}
                          className="text-[13.5px] font-medium text-amber underline underline-offset-2"
                        >
                          {localize(link, "label", appLocale)}
                        </Link>
                      </li>
                    ) : (
                      <li key={link.url}>
                        <a
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[13.5px] font-medium text-amber underline underline-offset-2"
                        >
                          {localize(link, "label", appLocale)}
                        </a>
                      </li>
                    ),
                  )}
                </ul>
              </aside>
            ) : null}
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
