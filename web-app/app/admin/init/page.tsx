"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { setupAdmin } from "@/lib/api"

export default function AdminInitPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    display_name: "",
  })

  const handleInit = async () => {
    setLoading(true)
    setError("")
    try {
      await setupAdmin(
        formData.email,
        formData.password,
        formData.display_name || undefined,
        formData.first_name || undefined,
        formData.last_name || undefined,
      )
      router.push("/admin/login")
    } catch (e: unknown) {
      setError((e as Error)?.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 sm:px-6 lg:px-8 py-8">
      <Card>
        <CardHeader>
          <CardTitle>Первый вход администратора</CardTitle>
          <CardDescription>
            Создайте учетную запись первого администратора системы
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="admin@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Пароль</Label>
            <Input
              id="password"
              type="password"
              placeholder="Минимум 8 символов"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="display_name">Отображаемое имя</Label>
            <Input
              id="display_name"
              type="text"
              placeholder="Администратор"
              value={formData.display_name}
              onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">Имя</Label>
              <Input
                id="first_name"
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Фамилия</Label>
              <Input
                id="last_name"
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              />
            </div>
          </div>

          <Button onClick={handleInit} disabled={loading} className="w-full">
            {loading ? "Создание..." : "Создать администратора"}
          </Button>
          
          <p className="text-xs text-muted-foreground text-center">
            Это действие доступно только один раз при первой настройке системы
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
