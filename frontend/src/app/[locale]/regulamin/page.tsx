import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";

import { MarkdownContent } from "@/components/markdown-content";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { apiFetch } from "@/lib/api";
import type { ContentPage } from "@/lib/types";

async function getPage(): Promise<ContentPage | null> {
  try {
    return await apiFetch<ContentPage>("/api/content-pages/regulamin/", { next: { revalidate: 60 } });
  } catch {
    return null;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const page = await getPage();
  if (!page) return {};
  const title = locale === "en" ? page.title_en : page.title_pl;
  const seoTitle = locale === "en" ? page.seo_title_en : page.seo_title_pl;
  const seoDescription = locale === "en" ? page.seo_description_en : page.seo_description_pl;
  return {
    title: seoTitle || title,
    description: seoDescription || undefined,
  };
}

export default async function RegulaminPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);
  const page = await getPage();

  const title = page ? (locale === "en" ? page.title_en : page.title_pl) : "Regulamin";
  const body = page ? (locale === "en" ? page.body_en : page.body_pl) : "";

  return (
    <>
      <SiteHeader />
      <main className="mx-auto max-w-[900px] px-6 py-16">
        <h1 className="font-heading mb-8 text-2xl font-semibold">{title}</h1>
        {body && <MarkdownContent markdown={body} />}
      </main>
      <SiteFooter />
    </>
  );
}
