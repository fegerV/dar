"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Check, Copy, Share2, ExternalLink } from "lucide-react"

interface ShareResultProps {
  publicUrl: string
  videoUrl: string | null
  thumbnailUrl: string | null
  title: string
  durationSec?: number | null
  referralCode?: string | null
}

export function ShareResult({
  publicUrl,
  videoUrl,
  thumbnailUrl,
  title,
  durationSec,
  referralCode,
}: ShareResultProps) {
  const { t } = useTranslation()
  const [copied, setCopied] = useState(false)

  const shareUrl = publicUrl
  const encodedUrl = encodeURIComponent(shareUrl)
  const encodedTitle = encodeURIComponent(title)

  const shareLinks = {
    telegram: `https://t.me/share/url?url=${encodedUrl}&text=${encodeURIComponent(
      "Check out this video generated with Daragent AI"
    )}`,
    twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(
      "Check out this video generated with Daragent AI"
    )}&url=${encodedUrl}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    whatsapp: `https://api.whatsapp.com/send?text=${encodeURIComponent(
      "Check out this video generated with Daragent AI"
    )}%20${encodedUrl}`,
    vk: `https://vk.com/share.php?url=${encodedUrl}&title=${encodedTitle}`,
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(shareUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>{t("share.title", "Share Your Creation")}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
          {videoUrl ? (
            <video
              src={videoUrl}
              poster={thumbnailUrl || ""}
              controls
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Share2 className="w-12 h-12 text-gray-400" />
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleCopy}
            className="flex-1"
          >
            {copied ? (
              <Check className="w-4 h-4 mr-2" />
            ) : (
              <Copy className="w-4 h-4 mr-2" />
            )}
            {copied ? t("share.copied", "Copied!") : t("share.copy_link", "Copy Link")}
          </Button>
          <Button
            variant="outline"
            onClick={() => window.open(shareUrl, "_blank")}
          >
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>

        <div className="space-y-2">
          <p className="text-sm text-gray-600">
            {t("share.subtitle", "Share to social media")}
          </p>
          <div className="grid grid-cols-5 gap-2">
            {Object.entries(shareLinks).map(([platform, url]) => (
              <Button
                key={platform}
                size="sm"
                onClick={() => window.open(url, "_blank", "width=600,height=400")}
              >
                {platform.charAt(0).toUpperCase() + platform.slice(1)}
              </Button>
            ))}
          </div>
        </div>

        {referralCode && (
          <div className="text-xs text-gray-500">
            {t("share.referral_code", "Shared with referral code:")} {referralCode}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
