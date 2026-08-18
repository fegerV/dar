"use client"

import React, { createContext, useContext, useEffect, useState, useCallback } from "react"
import type { AppState, User, Recipient, Greeting, Mood, Occasion, Concept, GreetingText, TemplateConcept, RatingValue } from "@/types"

const STORAGE_KEY = "daragent_app_state"

const initialState: AppState = {
  user: { photos: [], isOnboarded: false },
  recipients: [],
  currentGreeting: null,
  history: [],
}

function loadState(): AppState {
  if (typeof window === "undefined") return initialState
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return initialState
    const parsed = JSON.parse(raw)
    return { ...initialState, ...parsed }
  } catch {
    return initialState
  }
}

function saveState(state: AppState) {
  if (typeof window === "undefined") return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

interface AppStoreContextValue {
  state: AppState
  setUser: (user: Partial<User>) => void
  setUserPhoto: (photos: string[]) => void
  addRecipient: (recipient: Recipient) => void
  updateRecipient: (id: string, data: Partial<Recipient>) => void
  deleteRecipient: (id: string) => void
  setCurrentGreeting: (greeting: Greeting | null) => void
  updateCurrentGreeting: (data: Partial<Greeting>) => void
  saveCurrentGreeting: () => void
  completeCurrentGreeting: () => Greeting | undefined
  rateGreeting: (id: string, rating: RatingValue, feedback?: string) => void
  resetGreeting: () => void
}

const AppStoreContext = createContext<AppStoreContextValue | null>(null)

export function AppStoreProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>(initialState)

  useEffect(() => {
    setState(loadState())
  }, [])

  useEffect(() => {
    saveState(state)
  }, [state])

  const setUser = useCallback((user: Partial<User>) => {
    setState((prev) => ({ ...prev, user: { ...prev.user, ...user } }))
  }, [])

  const setUserPhoto = useCallback((photos: string[]) => {
    setState((prev) => ({ ...prev, user: { ...prev.user, photos } }))
  }, [])

  const addRecipient = useCallback((recipient: Recipient) => {
    setState((prev) => ({ ...prev, recipients: [...prev.recipients, recipient] }))
  }, [])

  const updateRecipient = useCallback((id: string, data: Partial<Recipient>) => {
    setState((prev) => ({
      ...prev,
      recipients: prev.recipients.map((r) => (r.id === id ? { ...r, ...data } : r)),
    }))
  }, [])

  const deleteRecipient = useCallback((id: string) => {
    setState((prev) => ({ ...prev, recipients: prev.recipients.filter((r) => r.id !== id) }))
  }, [])

  const setCurrentGreeting = useCallback((greeting: Greeting | null) => {
    setState((prev) => ({ ...prev, currentGreeting: greeting }))
  }, [])

  const updateCurrentGreeting = useCallback((data: Partial<Greeting>) => {
    setState((prev) => ({
      ...prev,
      currentGreeting: prev.currentGreeting ? { ...prev.currentGreeting, ...data } : null,
    }))
  }, [])

  const saveCurrentGreeting = useCallback(() => {
    setState((prev) => {
      if (!prev.currentGreeting) return prev
      return { ...prev, currentGreeting: prev.currentGreeting }
    })
  }, [])

  const completeCurrentGreeting = useCallback((): Greeting | undefined => {
    let completed: Greeting | undefined
    setState((prev) => {
      if (!prev.currentGreeting) return prev
      completed = {
        ...prev.currentGreeting,
        status: "completed",
        updatedAt: new Date().toISOString(),
      }
      return {
        ...prev,
        history: [...prev.history, completed],
        currentGreeting: null,
      }
    })
    return completed
  }, [])

  const rateGreeting = useCallback((id: string, rating: RatingValue, feedback?: string) => {
    setState((prev) => ({
      ...prev,
      history: prev.history.map((g) => (g.id === id ? { ...g, rating, feedback } : g)),
    }))
  }, [])

  const resetGreeting = useCallback(() => {
    setState((prev) => ({ ...prev, currentGreeting: null }))
  }, [])

  return (
    <AppStoreContext.Provider
      value={{
        state,
        setUser,
        setUserPhoto,
        addRecipient,
        updateRecipient,
        deleteRecipient,
        setCurrentGreeting,
        updateCurrentGreeting,
        saveCurrentGreeting,
        completeCurrentGreeting,
        rateGreeting,
        resetGreeting,
      }}
    >
      {children}
    </AppStoreContext.Provider>
  )
}

export function useAppStore() {
  const ctx = useContext(AppStoreContext)
  if (!ctx) throw new Error("useAppStore must be used within AppStoreProvider")
  return ctx
}
