"use client"

import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { PhotoUploader } from "@/components/photo-uploader"
import { Progress } from "@/components/ui/progress"
import { useAppStore } from "@/store/app-store"

export default function PhotosPage() {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, setUserPhoto } = useAppStore()

  const handleNext = () => {
    if (state.user.photos.length === 0) {
      return
    }
    setUserPhoto(state.user.photos)
    router.push("/onboarding/quality-check")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <div className="mb-6">
          <Progress value={50} aria-label="Step 2 of 4" className="h-2 mb-2" />
          <p className="text-sm text-muted-foreground text-center">Шаг 2 из 4</p>
        </div>

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

        {state.user.photos.length === 0 && (
          <p className="text-sm text-destructive mb-4">{t("onboarding.photos.min_photos_error")}</p>
        )}

        <div className="flex gap-3 pt-6">
          <Button variant="outline" onClick={() => router.back()} className="flex-1">
            {t("onboarding.photos.back")}
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
