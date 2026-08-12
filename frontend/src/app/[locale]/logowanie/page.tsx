import type { Metadata } from "next";
import { setRequestLocale } from "next-intl/server";

import { LoginForm } from "@/components/login-form";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  robots: {
    index: false,
    follow: false,
  },
};

export default async function LoginPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <>
      <SiteHeader />
      <main className="px-6 py-16">
        <LoginForm />
      </main>
      <SiteFooter />
    </>
  );
}
