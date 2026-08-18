"use client"

import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { BottomNav } from "@/components/bottom-nav"
import { useAppStore } from "@/store/app-store"

export default function PhotosPage() {
  const { t } = useTranslation()
  const { state } = useAppStore()

  return (
    <div className="min-h-screen bg-background pb-20 md:pb-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold mb-6">{t("photos.title")}</h1>
        {state.user.photos.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">{t("photos.no_photos")}</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {state.user.photos.map((photo, index) => (
              <div key={index} className="aspect-square rounded-lg overflow-hidden border">
                <img src={photo} alt={`Photo ${index + 1}`} className="w-full h-full object-cover" />
              </div>
            ))}
          </div>
        )}
      </div>
      <BottomNav />
    </div>
  )
}
