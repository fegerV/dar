"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { PhotoUploader } from "@/components/photo-uploader"
import { useAppStore } from "@/store/app-store"

export default function PhotosPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, setUserPhoto } = useAppStore()

  const handleNext = () => {
    setUserPhoto(state.user.photos)
    router.push("/onboarding/quality-check")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          ← {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-2">{t("onboarding.photos.title")}</h1>
        <p className="text-muted-foreground mb-6">{t("onboarding.photos.subtitle")}</p>

        <PhotoUploader
          photos={state.user.photos}
          onPhotosChange={setUserPhoto}
          min={1}
          max={10}
        />

        <div className="flex gap-3 pt-6">
          <Button variant="outline" onClick={() => router.back()} className="flex-1">
            {t("common.back")}
          </Button>
          <Button
            onClick={handleNext}
            disabled={state.user.photos.length === 0}
            className="flex-1"
          >
            {t("onboarding.photos.next")}
          </Button>
        </div>
      </div>
    </div>
  )
}
