import { useEffect, useRef, useState } from "react"

export interface AdminEvent {
  type: "stats" | "error" | string
  data?: Record<string, unknown>
  error?: string
  timestamp: string
}

export function useAdminEvents(enabled: boolean = true): AdminEvent | null {
  const [event, setEvent] = useState<AdminEvent | null>(null)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!enabled) return

    const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
    const url = `${base}/admin/events/stream-token`

    let es: EventSource
    try {
      es = new EventSource(url)
    } catch {
      return
    }

    es.onopen = () => {
      console.log("SSE connected")
    }

    es.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        setEvent(data)
      } catch {
        // ignore parse errors
      }
    }

    es.onerror = () => {
      es.close()
    }

    esRef.current = es

    return () => {
      es.close()
      esRef.current = null
    }
  }, [enabled])

  useEffect(() => {
    return () => {
      if (esRef.current) {
        esRef.current.close()
        esRef.current = null
      }
    }
  }, [])

  return event
}
