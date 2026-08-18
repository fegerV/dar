"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Sparkles } from "lucide-react"

export default function SplashPage() {
  const router = useRouter()

  useEffect(() => {
    const timer = setTimeout(() => {
      router.push("/welcome")
    }, 2000)
    return () => clearTimeout(timer)
  }, [router])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4">
      <div className="flex flex-col items-center space-y-4 text-center">
        <div className="flex items-center gap-2">
          <Sparkles className="h-12 w-12 text-primary" />
          <h1 className="text-4xl font-bold tracking-tight">ДАРАГЕНТ</h1>
        </div>
        <p className="text-lg text-muted-foreground">Подарки, которые невозможно забыть</p>
      </div>
    </div>
  )
}
