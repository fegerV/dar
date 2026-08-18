"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function AdminInitPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleInit = async () => {
    setLoading(true)
    setError("")
    try {
      const res = await fetch("/api/v1/admin/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || "Failed to init admin")
      }
      router.push("/admin/dashboard")
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 sm:px-6 lg:px-8 py-8">
      <Card>
        <CardHeader>
          <CardTitle>Admin initialization</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Create the first admin account. This action is available only once.
          </p>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button onClick={handleInit} disabled={loading} className="w-full">
            {loading ? "Initializing..." : "Become admin"}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
