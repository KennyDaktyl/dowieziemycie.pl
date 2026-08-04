import type { Metadata } from "next";
import { getLocale, getTranslations, setRequestLocale } from "next-intl/server";

import { Breadcrumbs } from "@/components/breadcrumbs";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { apiFetch } from "@/lib/api";
import { absoluteImageUrl } from "@/lib/images";
import { localize } from "@/lib/localize";
import { buildAlternates } from "@/lib/seo";
import type { BlogPost } from "@/lib/types";

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Blog" });
  return { title: t("heading"), description: t("lead"), alternates: buildAlternates("/blog", locale as AppLocale) };
}

export default async function BlogIndexPage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<{ q?: string }>;
}) {
  const { locale } = await params;
  const { q } = await searchParams;
  setRequestLocale(locale);

  const [t, tCrumbs, appLocale, allPosts] = await Promise.all([
    getTranslations("Blog"),
    getTranslations("Breadcrumbs"),
    getLocale() as Promise<AppLocale>,
    apiFetch<BlogPost[]>("/api/blog/", { next: { revalidate: 60 } }).catch(() => []),
  ]);

  const query = q?.trim().toLowerCase() ?? "";
  const posts = query
    ? allPosts.filter((post) => {
        const haystack = `${localize(post, "title", appLocale)} ${localize(post, "excerpt", appLocale)} ${localize(post, "body", appLocale)}`.toLowerCase();
        return haystack.includes(query);
      })
    : allPosts;

  return (
    <>
      <SiteHeader />
      <main>
        <div className="mx-auto max-w-[1200px] px-4 py-16 sm:px-6 sm:py-20">
          <Breadcrumbs items={[{ label: tCrumbs("home"), href: "/" }, { label: tCrumbs("blog") }]} />
          <h1 className="font-heading mt-3 text-[32px] font-semibold text-text sm:text-[42px]">{t("heading")}</h1>
          <p className="mt-3 max-w-[680px] text-[16px] leading-relaxed text-muted">{t("lead")}</p>

          <form action="/blog" method="get" className="mt-6 flex max-w-[480px] gap-2">
            <input
              type="search"
              name="q"
              defaultValue={q ?? ""}
              placeholder={t("searchPlaceholder")}
              className="flex-1 rounded-[10px] border border-line bg-panel px-4 py-2.5 text-[14px] text-text outline-none focus:border-amber"
            />
            <button
              type="submit"
              className="rounded-[10px] bg-amber px-5 py-2.5 text-[14px] font-semibold text-[#1a1305] transition-colors hover:brightness-105"
            >
              {t("searchSubmit")}
            </button>
          </form>

          {query ? (
            <p className="mt-3 text-[13px] text-muted">
              {t("searchResultsCount", { count: posts.length, query: q ?? "" })}{" "}
              <Link href="/blog" className="text-amber underline">
                {t("searchClear")}
              </Link>
            </p>
          ) : null}

          <div className="mt-10 grid grid-cols-1 gap-5 lg:grid-cols-2">
            {posts.length === 0 ? <p className="text-muted">{t("searchNoResults")}</p> : null}
            {posts.map((post) => {
              const tag = localize(post, "tag", appLocale);
              const title = localize(post, "title", appLocale);
              const excerpt = localize(post, "excerpt", appLocale);

              return (
                <Link
                  key={post.slug}
                  href={`/blog/${post.slug}`}
                  className="flex min-h-[220px] flex-col overflow-hidden rounded-[14px] border border-line bg-panel transition-transform hover:-translate-y-0.5"
                >
                  {post.cover_image ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={absoluteImageUrl(post.cover_image)} alt={title} className="h-44 w-full object-cover" />
                  ) : null}
                  <div className="flex flex-1 flex-col gap-2 p-5">
                    <div className="flex items-center gap-3 text-[13px] text-muted">
                      {tag ? <span className="font-medium text-amber">{tag}</span> : null}
                      <time dateTime={post.published_at}>{post.published_at}</time>
                    </div>
                    <h2 className="font-heading text-[20px] font-semibold text-text">{title}</h2>
                    {excerpt ? <p className="text-[14px] leading-relaxed text-muted">{excerpt}</p> : null}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
