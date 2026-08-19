import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const ADMIN_PATHS = ["/admin/dashboard", "/admin/orders", "/admin/generations", "/admin/queue", "/admin/users", "/admin/templates", "/admin/payments", "/admin/workers", "/admin/system"]

export function middleware(request: NextRequest) {
  const locale = request.nextUrl.searchParams.get("locale") || "ru"
  const response = NextResponse.redirect(new URL(`/${locale}${request.nextUrl.pathname}`, request.url))
  response.cookies.set("locale", locale, { path: "/", maxAge: 60 * 60 * 24 * 365 })

  if (request.nextUrl.pathname.startsWith("/admin") && !request.nextUrl.pathname.startsWith("/admin/login") && !request.nextUrl.pathname.startsWith("/admin/init") && !request.nextUrl.pathname.startsWith("/admin/setup")) {
     const token = request.cookies.get("daragent_admin_access")?.value
    if (!token) {
      return NextResponse.redirect(new URL("/admin/login", request.url))
    }
  }

  return response
}

export const config = {
  matcher: ["/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)"],
}
