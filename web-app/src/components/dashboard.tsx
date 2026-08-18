"use client"

import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PlusCircle, ShoppingBag, Heart, Play } from "lucide-react"

const projects = [
  { id: "1", title: "День рождения мамы", status: "active", updatedAt: "2026-08-18" },
  { id: "2", title: "С новым годом!", status: "completed", updatedAt: "2026-08-10" },
  { id: "3", title: "Юбилей папы", status: "archived", updatedAt: "2026-07-22" },
]

export function DashboardScreen() {
  const { t } = useTranslation()

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">{t("dashboard.title")}</h1>
        <p className="text-muted-foreground mt-2">{t("dashboard.subtitle")}</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="h-5 w-5" aria-hidden="true" />
              {t("dashboard.active")}
            </CardTitle>
            <CardDescription>{projects.filter((p) => p.status === "active").length} проекта</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {projects
                .filter((p) => p.status === "active")
                .map((p) => (
                  <li key={p.id} className="flex items-center justify-between">
                    <span>{p.title}</span>
                    <span className="text-xs text-muted-foreground">{p.updatedAt}</span>
                  </li>
                ))}
            </ul>
          </CardContent>
          <CardFooter>
            <Button className="w-full" asChild>
              <a href="/create">
                <PlusCircle className="h-4 w-4 mr-2" aria-hidden="true" />
                {t("dashboard.new_greeting")}
              </a>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingBag className="h-5 w-5" aria-hidden="true" />
              {t("dashboard.purchases")}
            </CardTitle>
            <CardDescription>История покупок</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Покупок пока нет</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5" aria-hidden="true" />
              {t("dashboard.favorites")}
            </CardTitle>
            <CardDescription>Избранные получатели</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Список пуст</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
