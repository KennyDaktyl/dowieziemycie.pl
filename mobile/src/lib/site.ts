export const SITE_LABELS: Record<string, string> = {
  dowieziemycie: "dowieziemycie.pl",
  transfer247: "transfer247.pl",
};

export function siteLabel(site: string): string {
  return SITE_LABELS[site] ?? site;
}
