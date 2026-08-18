import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  const locale = request.nextUrl.searchParams.get("locale") || "ru"
  const response = NextResponse.redirect(new URL(`/${locale}${request.nextUrl.pathname}`, request.url))
  response.cookies.set("locale", locale, { path: "/", maxAge: 60 * 60 * 24 * 365 })

  if (request.nextUrl.pathname.startsWith("/admin")) {
    const session = request.cookies.get("session")?.value
    if (!session) {
      return NextResponse.redirect(new URL("/onboarding", request.url))
    }
  }

  return response
}

export const config = {
  matcher: ["/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)"],
}
