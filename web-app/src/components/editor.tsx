"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Select } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Save, RotateCcw, History } from "lucide-react"

const models = ["grok", "kling", "veo"]

export function EditorScreen({ generationId }: { generationId: string }) {
  const { t } = useTranslation()
  const [prompt, setPrompt] = useState("")
  const [negative, setNegative] = useState("")
  const [model, setModel] = useState(models[0])
  const [saving, setSaving] = useState(false)
  const [versions] = useState([
    { id: "1", prompt: "Initial prompt", model: "grok", createdAt: "2026-08-18 10:00" },
    { id: "2", prompt: "Updated prompt", model: "grok", createdAt: "2026-08-18 11:30" },
  ])

  const handleSave = async () => {
    setSaving(true)
    await new Promise((resolve) => setTimeout(resolve, 800))
    setSaving(false)
  }

  const handleRegenerate = async () => {
    await new Promise((resolve) => setTimeout(resolve, 1200))
  }

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">{t("editor.title")}</h1>
        <p className="text-muted-foreground mt-1">Generation #{generationId}</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>{t("editor.prompt")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={t("editor.prompt")}
                aria-label={t("editor.prompt")}
                className="min-h-[120px]"
              />
              <div>
                <label className="block text-sm font-medium mb-2" htmlFor="negative-prompt">
                  {t("editor.negative")}
                </label>
                <Textarea
                  id="negative-prompt"
                  value={negative}
                  onChange={(e) => setNegative(e.target.value)}
                  placeholder={t("editor.negative")}
                  aria-label={t("editor.negative")}
                  className="min-h-[80px]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" htmlFor="model-select">
                  {t("editor.model")}
                </label>
                <Select value={model} onValueChange={setModel} id="model-select" aria-label={t("editor.model")}>
                  {models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </Select>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Button onClick={handleSave} disabled={saving} className="flex-1">
              <Save className="h-4 w-4 mr-2" aria-hidden="true" />
              {saving ? "Saving..." : t("editor.save")}
            </Button>
            <Button variant="outline" onClick={handleRegenerate} className="flex-1">
              <RotateCcw className="h-4 w-4 mr-2" aria-hidden="true" />
              {t("editor.regenerate")}
            </Button>
          </div>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" aria-hidden="true" />
                {t("editor.history")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {versions.map((v) => (
                  <li key={v.id} className="flex items-start justify-between rounded-md border p-3">
                    <div>
                      <p className="text-sm font-medium">#{v.id}</p>
                      <p className="text-xs text-muted-foreground line-clamp-2">{v.prompt}</p>
                      <p className="text-xs text-muted-foreground mt-1">{v.createdAt}</p>
                    </div>
                    <span className="text-xs bg-muted px-2 py-1 rounded">{v.model}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Overall</span>
                  <span>93%</span>
                </div>
                <Progress value={93} aria-label="Quality score 93%" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
