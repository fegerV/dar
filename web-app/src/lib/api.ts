const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const ACCESS_COOKIE_NAME = "daragent_admin_access"
const REFRESH_COOKIE_NAME = "daragent_admin_refresh"

interface Tokens {
  access: string
  refresh: string
}

function getCookie(name: string): string | null {
  if (typeof window === "undefined") return null
  const cookies = document.cookie.split("; ")
  for (const cookie of cookies) {
    const [key, ...parts] = cookie.split("=")
    if (key === name) return decodeURIComponent(parts.join("="))
  }
  return null
}

function setCookie(name: string, value: string, maxAgeSec: number): void {
  if (typeof window === "undefined") return
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSec}; SameSite=Lax; Secure=${location.protocol === "https:"}`
}

function clearCookie(name: string): void {
  document.cookie = `${name}=; path=/; max-age=0; SameSite=Lax; Secure=${location.protocol === "https:"}`
}

function getAccessToken(): string | null {
  return getCookie(ACCESS_COOKIE_NAME)
}

function getRefreshToken(): string | null {
  return getCookie(REFRESH_COOKIE_NAME)
}

function setTokens(tokens: Tokens): void {
  setCookie(ACCESS_COOKIE_NAME, tokens.access, 3600)
  setCookie(REFRESH_COOKIE_NAME, tokens.refresh, 86400)
}

function clearTokens(): void {
  clearCookie(ACCESS_COOKIE_NAME)
  clearCookie(REFRESH_COOKIE_NAME)
}

function getClientAccessToken(): string | null {
  return getAccessToken()
}

export function setAuthTokens(access: string, refresh: string): void {
  setTokens({ access, refresh })
}

export function clearAuthTokens(): void {
  clearTokens()
}

export async function login(email: string, password: string): Promise<Tokens> {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || "Login failed")
  }
  const data = await res.json()
  const tokens = { access: data.access_token, refresh: data.refresh_token }
  setTokens(tokens)
  return tokens
}

export function logout(): void {
  clearTokens()
  if (typeof window !== "undefined") {
    window.location.href = "/admin/login"
  }
}

let isRefreshing = false
let pendingRequests: Array<{
  resolve: (token: string) => void
  reject: (err: Error) => void
}> = []

async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) throw new Error("No refresh token")

  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      pendingRequests.push({ resolve, reject })
    })
  }

  isRefreshing = true
  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!res.ok) throw new Error("Token refresh failed")
    const data = await res.json()
    const newAccess = data.access_token
    const newRefresh = data.refresh_token || refreshToken
    setTokens({ access: newAccess, refresh: newRefresh })

    pendingRequests.forEach((req) => req.resolve(newAccess))
    return newAccess
  } catch (err) {
    pendingRequests.forEach((req) => req.reject(err as Error))
    clearTokens()
    throw err
  } finally {
    isRefreshing = false
    pendingRequests = []
  }
}

export async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const accessToken = getAccessToken()
  const headers = new Headers(options.headers)

  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`)
  }

  if (["POST", "PUT", "PATCH", "DELETE"].includes(options.method || "GET")) {
    headers.set("X-Requested-With", "XMLHttpRequest")
  }

  let res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers, credentials: "include" })

  if (res.status === 401 && getRefreshToken()) {
    const newAccess = await refreshAccessToken().catch(() => null)
    if (newAccess) {
      headers.set("Authorization", `Bearer ${newAccess}`)
      res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers, credentials: "include" })
    }
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `API error: ${res.status}`)
  }

  return res.json() as T
}

export type { Tokens }
export { API_BASE_URL, getClientAccessToken }
