const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const TOKEN_STORAGE_KEY = "daragent_admin_token"
const REFRESH_STORAGE_KEY = "daragent_admin_refresh"

interface Tokens {
  access: string
  refresh: string
}

function getTokens(): Tokens | null {
  if (typeof window === "undefined") return null
  const access = localStorage.getItem(TOKEN_STORAGE_KEY)
  const refresh = localStorage.getItem(REFRESH_STORAGE_KEY)
  if (!access || !refresh) return null
  return { access, refresh }
}

function setTokens(tokens: Tokens): void {
  if (typeof window === "undefined") return
  localStorage.setItem(TOKEN_STORAGE_KEY, tokens.access)
  localStorage.setItem(REFRESH_STORAGE_KEY, tokens.refresh)
  document.cookie = `${TOKEN_STORAGE_KEY}=${tokens.access}; path=/; max-age=3600`
}

function clearTokens(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(TOKEN_STORAGE_KEY)
  localStorage.removeItem(REFRESH_STORAGE_KEY)
  document.cookie = `${TOKEN_STORAGE_KEY}=; path=/; max-age=0`
}

export function getAccessToken(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem(TOKEN_STORAGE_KEY) : null
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
  const tokens = getTokens()
  if (!tokens?.refresh) throw new Error("No refresh token")

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
      body: JSON.stringify({ refresh_token: tokens.refresh }),
    })
    if (!res.ok) throw new Error("Token refresh failed")
    const data = await res.json()
    const newAccess = data.access_token
    const newRefresh = data.refresh_token || tokens.refresh
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
  const tokens = getTokens()
  const headers = new Headers(options.headers)

  if (tokens?.access) {
    headers.set("Authorization", `Bearer ${tokens.access}`)
  }

  let res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })

  if (res.status === 401 && tokens?.refresh) {
    const newAccess = await refreshAccessToken().catch(() => null)
    if (newAccess) {
      headers.set("Authorization", `Bearer ${newAccess}`)
      res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
    }
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || `API error: ${res.status}`)
  }

  return res.json() as T
}

export type { Tokens }
export { API_BASE_URL }
