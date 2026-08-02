import { getTranslations } from "next-intl/server";

import { Link } from "@/i18n/navigation";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default async function NotFound() {
  const [t, tNav] = await Promise.all([getTranslations("NotFound"), getTranslations("Nav")]);

  const links = [
    { href: "/#routes", label: tNav("routes") },
    { href: "/cennik", label: tNav("pricing") },
    { href: "/na-zywo", label: tNav("tracking") },
    { href: "/blog", label: tNav("blog") },
  ];

  return (
    <>
      <SiteHeader />
      <main>
        <div className="mx-auto max-w-[640px] px-4 py-24 text-center sm:px-6">
          <div className="text-amber font-heading text-[64px] font-bold">404</div>
          <h1 className="font-heading mt-2 text-[26px] font-semibold">{t("title")}</h1>
          <p className="mt-3 text-[15px] text-muted">{t("lead")}</p>

          <Link
            href="/"
            className="bg-amber mt-8 inline-block rounded-md px-6 py-3 text-[14px] font-semibold text-[#1a1305] transition-transform hover:-translate-y-px"
          >
            {t("backHome")}
          </Link>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4 text-[14px]">
            {links.map((link) => (
              <a key={link.href} href={link.href} className="text-amber font-medium hover:underline">
                {link.label}
              </a>
            ))}
          </div>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
