import { redirect } from "@/i18n/navigation";

// Superseded — /logowanie now detects driver vs. customer by phone number,
// so there's no separate driver-specific login entry point anymore. Kept as
// a redirect since the URL was linked from the footer for a while.
export default async function DriverLoginRedirect({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  redirect({ href: "/logowanie", locale });
}
