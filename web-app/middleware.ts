import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const locale = request.nextUrl.searchParams.get("locale") || "ru"
  const response = NextResponse.redirect(new URL(`/${locale}${request.nextUrl.pathname}`, request.url))
  response.cookies.set("locale", locale, { path: "/", maxAge: 60 * 60 * 24 * 365 })
  return response
}

export const config = {
  matcher: ["/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)"],
}
