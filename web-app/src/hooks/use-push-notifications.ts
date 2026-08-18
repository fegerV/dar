"use client"

import { useEffect, useRef } from "react"

export function usePushNotifications() {
  const registrationRef = useRef<ServiceWorkerRegistration | null>(null)

  useEffect(() => {
    if (typeof window === "undefined" || !("serviceWorker" in navigator) || !("PushManager" in window)) {
      return
    }

    async function register() {
      try {
        const registration = await navigator.serviceWorker.register("/sw.js")
        registrationRef.current = registration
        const permission = await Notification.requestPermission()
        if (permission === "granted") {
          console.log("Push notifications granted")
        }
      } catch (error) {
        console.error("Push registration failed", error)
      }
    }

    register()
  }, [])

  const send = async (payload: { title: string; body: string }) => {
    if (!registrationRef.current?.pushManager) return
    // Placeholder for actual push subscription logic
    console.log("Push payload", payload)
  }

  return { send }
}
