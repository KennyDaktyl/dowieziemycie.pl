import createIntlMiddleware from "next-intl/middleware";

import { routing } from "./i18n/routing";

const intlMiddleware = createIntlMiddleware(routing);

// Next.js 16 renamed the `middleware.ts` file convention to `proxy.ts`
// (exported function `proxy` instead of `middleware`) — next-intl's own
// APIs are unaffected, we just export its handler under the new name.
export function proxy(request: Parameters<typeof intlMiddleware>[0]) {
  return intlMiddleware(request);
}

export const config = {
  matcher: ["/((?!api|_next|.*\\..*).*)"],
};
