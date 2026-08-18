"use client"

import { useTranslation } from "react-i18next"

export function Toast() {
  const { t } = useTranslation()

  return (
    <div
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="fixed bottom-4 right-4 z-50 hidden"
      id="toast-container"
    >
      <div className="rounded-lg border bg-background p-4 shadow-lg">
        <p className="text-sm font-medium">{t("notification.title")}</p>
      </div>
    </div>
  )
}
