import { useState, useEffect, useCallback } from "react"
import { useTranslation } from "react-i18next"
import { apiFetch } from "@/lib/api"
import { useToast } from "@/components/ui/toast"

export interface UseAdminListOptions<T> {
  endpoint: string
  page?: number
  pageSize?: number
  filters?: Record<string, string | number | boolean | undefined>
  transform?: (data: unknown) => T[]
  onSuccess?: (items: T[]) => void
  onError?: (error: Error) => void
}

export interface UseAdminListResult<T> {
  items: T[]
  loading: boolean
  error: string | null
  page: number
  pageSize: number
  total: number
  totalPages: number
  setPage: (page: number) => void
  setPageSize: (pageSize: number) => void
  setFilters: (filters: Record<string, string | number | boolean | undefined>) => void
  refetch: () => void
}

export function useAdminList<T>({
  endpoint,
  page: initialPage = 1,
  pageSize: initialPageSize = 20,
  filters = {},
  transform = (data) => data as T[],
  onSuccess,
  onError,
}: UseAdminListOptions<T>): UseAdminListResult<T> {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [items, setItems] = useState<T[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(initialPage)
  const [pageSize, setPageSize] = useState(initialPageSize)
  const [total, setTotal] = useState(0)
  const [activeFilters, setActiveFilters] = useState(filters)

  const buildQueryString = useCallback(
    (params: Record<string, unknown>) => {
      const searchParams = new URLSearchParams()
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "") {
          searchParams.set(key, String(value))
        }
      })
      const qs = searchParams.toString()
      return qs ? `?${qs}` : ""
    },
    []
  )

  const fetchData = useCallback(
    async (currentPage: number, currentPageSize: number, currentFilters: Record<string, string | number | boolean | undefined>) => {
      setLoading(true)
      setError(null)
      try {
        const qs = buildQueryString({
          page: currentPage,
          page_size: currentPageSize,
          ...currentFilters,
        })
        const raw = await apiFetch<unknown>(`${endpoint}${qs}`)
        let data: T[]
        let total = 0

        if (
          typeof raw === "object" &&
          raw !== null &&
          "items" in raw &&
          "total" in raw &&
          Array.isArray((raw as Record<string, unknown>).items)
        ) {
          data = transform((raw as Record<string, unknown>).items)
          total = (raw as Record<string, unknown>).total as number
        } else {
          data = transform(raw)
          total = data.length
        }

        setItems(data)
        setTotal(total)
        onSuccess?.(data)
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load data"
        setError(message)
        onError?.(err instanceof Error ? err : new Error(message))
        toast({
          title: t("notification.error") || "Error",
          description: message,
          variant: "error",
        })
      } finally {
        setLoading(false)
      }
    },
    [endpoint, transform, onSuccess, onError, toast, t, buildQueryString]
  )

  useEffect(() => {
    fetchData(page, pageSize, activeFilters)
  }, [page, pageSize, activeFilters, fetchData])

  const setFilters = useCallback((newFilters: Record<string, string | number | boolean | undefined>) => {
    setActiveFilters(newFilters)
    setPage(1)
  }, [])

  const refetch = useCallback(() => {
    fetchData(page, pageSize, activeFilters)
  }, [page, pageSize, activeFilters, fetchData])

  return {
    items,
    loading,
    error,
    page,
    pageSize,
    total,
    totalPages: Math.max(1, Math.ceil(total / pageSize)),
    setPage,
    setPageSize: (size: number) => {
      setPageSize(size)
      setPage(1)
    },
    setFilters,
    refetch,
  }
}
