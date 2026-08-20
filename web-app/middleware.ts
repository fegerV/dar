import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const ADMIN_PATHS = ["/admin/dashboard", "/admin/orders", "/admin/generations", "/admin/queue", "/admin/users", "/admin/templates", "/admin/payments", "/admin/workers", "/admin/system", "/admin/help"]

const SUPPORTED_LOCALES = ["ru", "en"]

export function middleware(request: NextRequest) {
  const { pathname, searchParams } = request.nextUrl
  const locale = searchParams.get("locale") || "ru"

  if (pathname.startsWith("/admin") && !pathname.startsWith("/admin/login") && !pathname.startsWith("/admin/init") && !pathname.startsWith("/admin/setup")) {
    const token = request.cookies.get("daragent_admin_access")?.value
    if (!token) {
      return NextResponse.redirect(new URL(`/${locale}/admin/login?locale=${locale}`, request.url))
    }
  }

  const response = NextResponse.next()
  response.cookies.set("locale", locale, { path: "/", maxAge: 60 * 60 * 24 * 365 })

  return response
}

export const config = {
  matcher: ["/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)"],
}
