"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Plus, Trash2, Zap, Check, X, Loader2 } from "lucide-react"
import { apiFetch } from "@/lib/api"
import { useRouter } from "next/navigation"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { useTranslation } from "react-i18next"
import { useAdminList } from "@/hooks/use-admin-list"
import { Pagination } from "@/components/admin/pagination"
import { useToast } from "@/components/ui/toast"

interface AIProvider {
  id: string
  name: string
  provider_type: string
  base_url: string
  enabled: boolean
  priority: number
  default_model: string | null
  config: Record<string, unknown>
  last_tested_at: string | null
  last_test_status: string | null
  last_test_message: string | null
}

interface AIModel {
  id: string
  provider_id: string
  name: string
  display_name: string
  model_type: string
  model_id: string
  max_prompt_length: number
  supports_images: boolean
  supports_video: boolean
  supports_audio: boolean
  default_parameters: Record<string, unknown>
  cost_per_unit: number
  unit_type: string
  enabled: boolean
  is_default: boolean
  config: Record<string, unknown>
}

const MODEL_TYPES = [
  { value: "chat", label: "Chat (Text/LLM)" },
  { value: "image", label: "Image Generation" },
  { value: "video_lite", label: "Video (Lite)" },
  { value: "video_premium", label: "Video (Premium)" },
  { value: "voice", label: "Voice / TTS" },
  { value: "music", label: "Music Generation" },
]

const POLZA_VIDEO_MODELS = [
  { model_id: "bytedance/seedance-2", display_name: "Seedance 2", tier: "video_premium" },
  { model_id: "bytedance/seedance-2-fast", display_name: "Seedance 2 Fast", tier: "video_lite" },
  { model_id: "bytedance/seedance-2-mini", display_name: "Seedance 2 Mini", tier: "video_lite" },
]

const POLZA_IMAGE_MODELS = [
  { model_id: "bytedance/seedream-5-lite", display_name: "Seedream 5.0 Lite" },
  { model_id: "bytedance/seedream-4-5", display_name: "Seedream 4.5" },
  { model_id: "bytedance/seedream-4", display_name: "Seedream 4" },
  { model_id: "bytedance/seedream-3", display_name: "Seedream 3.0" },
  { model_id: "openai/gpt-image-1-5", display_name: "GPT Image 1.5" },
  { model_id: "openai/gpt-image-2", display_name: "GPT Image 2" },
  { model_id: "xai/grok-imagine", display_name: "Grok Imagine" },
  { model_id: "alibaba/qwen-image", display_name: "Qwen Image" },
  { model_id: "black-forest-labs/flux-2-pro", display_name: "Flux-2 Pro" },
  { model_id: "black-forest-labs/flux-2-flex", display_name: "Flux-2 Flex" },
  { model_id: "nanobanana/nano-banana", display_name: "Nano Banana" },
  { model_id: "nanobanana/nano-banana-pro", display_name: "Nano Banana Pro" },
  { model_id: "nanobanana/nano-banana-2", display_name: "Nano Banana 2" },
]

const POLZA_LLM_MODELS = [
  { model_id: "anthropic/claude-opus-4", display_name: "Claude Opus 4" },
  { model_id: "anthropic/claude-sonnet-4", display_name: "Claude Sonnet 4" },
  { model_id: "anthropic/claude-haiku-3-5", display_name: "Claude Haiku 3.5" },
  { model_id: "openai/gpt-5", display_name: "GPT-5" },
  { model_id: "openai/gpt-5-mini", display_name: "GPT-5 Mini" },
  { model_id: "google/gemini-2-5-pro", display_name: "Gemini 2.5 Pro" },
  { model_id: "google/gemini-2-5-flash", display_name: "Gemini 2.5 Flash" },
  { model_id: "deepseek/deepseek-v3", display_name: "DeepSeek V3" },
  { model_id: "alibaba/qwen-3-max", display_name: "Qwen 3 Max" },
]

export function AdminAIModels() {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [providers, setProviders] = useState<AIProvider[]>([])
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null)
  const [creatingProvider, setCreatingProvider] = useState(false)
  const [creatingModel, setCreatingModel] = useState(false)
  const [testingProvider, setTestingProvider] = useState<string | null>(null)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  const loadProviders = useCallback(async () => {
    try {
      const data = await apiFetch<AIProvider[]>("/admin/ai/providers")
      setProviders(data)
    } catch {
      // error handled by API
    }
  }, [])

  const { items: models, loading: modelsLoading, page, pageSize, total, setPage, setPageSize, setFilters, refetch: refetchModels } = useAdminList<AIModel>({
    endpoint: "/admin/ai/models",
    pageSize: 20,
    filters: selectedProvider ? { provider_id: selectedProvider } : {},
    transform: (raw) => {
      const paginated = raw as { items: AIModel[]; total: number; page: number; page_size: number }
      return paginated.items
    },
  })

  useEffect(() => {
    setFilters(selectedProvider ? { provider_id: selectedProvider } : {})
  }, [selectedProvider, setFilters])

  useEffect(() => {
    if (user) {
      loadProviders()
    }
  }, [user, loadProviders])

  const handleTestProvider = async (providerId: string) => {
    setTestingProvider(providerId)
    try {
      await apiFetch(`/admin/ai/providers/${providerId}/test`, { method: "POST" })
      await loadProviders()
      toast({
        title: t("notification.success") || "Success",
        description: "Provider test completed",
        variant: "success",
      })
    } catch {
      toast({
        title: t("notification.error") || "Error",
        description: "Provider test failed",
        variant: "error",
      })
    } finally {
      setTestingProvider(null)
    }
  }

  const handleDeleteProvider = async (providerId: string) => {
    if (!confirm("Delete this provider and all its models?")) return
    try {
      await apiFetch(`/admin/ai/providers/${providerId}`, { method: "DELETE" })
      toast({
        title: t("notification.success") || "Success",
        description: "Provider deleted",
        variant: "success",
      })
      await loadProviders()
      if (selectedProvider === providerId) setSelectedProvider(null)
    } catch {
      toast({
        title: t("notification.error") || "Error",
        description: "Failed to delete provider",
        variant: "error",
      })
    }
  }

  const handleDeleteModel = async (modelId: string) => {
    if (!confirm("Delete this model?")) return
    try {
      await apiFetch(`/admin/ai/models/${modelId}`, { method: "DELETE" })
      toast({
        title: t("notification.success") || "Success",
        description: "Model deleted",
        variant: "success",
      })
      refetchModels()
    } catch {
      toast({
        title: t("notification.error") || "Error",
        description: "Failed to delete model",
        variant: "error",
      })
    }
  }

  const loading = authLoading

  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.ai_models")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.ai_models")}</p>
        </div>
        <Card>
          <CardContent>
            <p className="py-8 text-center text-muted-foreground">Loading...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t("admin.sidebar.ai_models")}</h1>
          <p className="text-muted-foreground mt-1">{t("admin.pages.ai_models")}</p>
        </div>
        <Button onClick={() => setCreatingProvider(true)}>
          <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
          Add Provider
        </Button>
      </div>

      {creatingProvider && (
        <ProviderForm
          onCancel={() => setCreatingProvider(false)}
          onSuccess={async () => {
            setCreatingProvider(false)
            await loadProviders()
          }}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Providers</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {providers.length === 0 && (
                <p className="text-sm text-muted-foreground">No providers configured</p>
              )}
              {providers.map((provider) => (
                <div
                  key={provider.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedProvider === provider.id
                      ? "border-primary bg-primary/5"
                      : "hover:bg-muted/50"
                  }`}
                  onClick={() => setSelectedProvider(provider.id)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{provider.name}</span>
                      {provider.enabled ? (
                        <Badge className="bg-green-100 text-green-800 text-xs">Active</Badge>
                      ) : (
                        <Badge variant="secondary" className="text-xs">Disabled</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleTestProvider(provider.id)
                        }}
                        disabled={testingProvider === provider.id}
                      >
                        {testingProvider === provider.id ? (
                          <Loader2 className="h-3 w-3 animate-spin" />
                        ) : (
                          <Zap className="h-3 w-3" />
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteProvider(provider.id)
                        }}
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                  {provider.last_test_status && (
                    <div className="flex items-center gap-1 mt-1 text-xs">
                      {provider.last_test_status === "ok" ? (
                        <Check className="h-3 w-3 text-green-600" />
                      ) : (
                        <X className="h-3 w-3 text-red-600" />
                      )}
                      <span className={provider.last_test_status === "ok" ? "text-green-600" : "text-red-600"}>
                        {provider.last_test_message}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              {selectedProvider
                ? `Models (${providers.find((p) => p.id === selectedProvider)?.name})`
                : "All Models"}
            </h2>
            <div className="flex items-center gap-2">
              <Select
                value={selectedProvider || "all"}
                onValueChange={(v) => setSelectedProvider(v === "all" ? null : v)}
                className="w-48"
                aria-label="Filter by provider"
              >
                <option value="all">All Providers</option>
                {providers.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </Select>
              <Button size="sm" onClick={() => setCreatingModel(true)} disabled={providers.length === 0}>
                <Plus className="h-4 w-4 mr-1" aria-hidden="true" />
                Add Model
              </Button>
            </div>
          </div>

          {selectedProvider && providers.find((p) => p.id === selectedProvider)?.provider_type === "polza" && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Quick Add Polza.ai Models</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="text-xs font-semibold mb-2">Video Models (Seedance 2)</h3>
                  <div className="flex flex-wrap gap-2">
                    {POLZA_VIDEO_MODELS.map((m) => (
                      <Button
                        key={m.model_id}
                        size="sm"
                        variant="outline"
                        onClick={async () => {
                          try {
                            await apiFetch("/admin/ai/models", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({
                                provider_id: selectedProvider,
                                name: m.model_id.split("/")[1],
                                display_name: m.display_name,
                                model_type: m.tier,
                                model_id: m.model_id,
                                max_prompt_length: 20000,
                                supports_images: true,
                                supports_video: true,
                                supports_audio: true,
                                cost_per_unit: 0.5,
                                unit_type: "second",
                                enabled: true,
                                is_default: false,
                              }),
                            })
                            toast({
                              title: t("notification.success") || "Success",
                              description: `${m.display_name} added`,
                              variant: "success",
                            })
                            refetchModels()
                          } catch {
                            toast({
                              title: t("notification.error") || "Error",
                              description: `Failed to add ${m.display_name}`,
                              variant: "error",
                            })
                          }
                        }}
                      >
                        + {m.display_name}
                      </Button>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-xs font-semibold mb-2">Image Models</h3>
                  <div className="flex flex-wrap gap-2">
                    {POLZA_IMAGE_MODELS.map((m) => (
                      <Button
                        key={m.model_id}
                        size="sm"
                        variant="outline"
                        onClick={async () => {
                          try {
                            await apiFetch("/admin/ai/models", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({
                                provider_id: selectedProvider,
                                name: m.model_id.split("/")[1].replace(/-/g, "_"),
                                display_name: m.display_name,
                                model_type: "image",
                                model_id: m.model_id,
                                max_prompt_length: 5000,
                                supports_images: false,
                                supports_video: false,
                                supports_audio: false,
                                cost_per_unit: 0.1,
                                unit_type: "image",
                                enabled: true,
                                is_default: false,
                              }),
                            })
                            toast({
                              title: t("notification.success") || "Success",
                              description: `${m.display_name} added`,
                              variant: "success",
                            })
                            refetchModels()
                          } catch {
                            toast({
                              title: t("notification.error") || "Error",
                              description: `Failed to add ${m.display_name}`,
                              variant: "error",
                            })
                          }
                        }}
                      >
                        + {m.display_name}
                      </Button>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-xs font-semibold mb-2">LLM Models</h3>
                  <div className="flex flex-wrap gap-2">
                    {POLZA_LLM_MODELS.map((m) => (
                      <Button
                        key={m.model_id}
                        size="sm"
                        variant="outline"
                        onClick={async () => {
                          try {
                            await apiFetch("/admin/ai/models", {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({
                                provider_id: selectedProvider,
                                name: m.model_id.split("/")[1].replace(/\./g, "_").replace(/-/g, "_"),
                                display_name: m.display_name,
                                model_type: "chat",
                                model_id: m.model_id,
                                max_prompt_length: 200000,
                                supports_images: true,
                                supports_video: false,
                                supports_audio: false,
                                cost_per_unit: 0.000001,
                                unit_type: "token",
                                enabled: true,
                                is_default: false,
                              }),
                            })
                            toast({
                              title: t("notification.success") || "Success",
                              description: `${m.display_name} added`,
                              variant: "success",
                            })
                            refetchModels()
                          } catch {
                            toast({
                              title: t("notification.error") || "Error",
                              description: `Failed to add ${m.display_name}`,
                              variant: "error",
                            })
                          }
                        }}
                      >
                        + {m.display_name}
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {creatingModel && (
            <ModelForm
              providers={providers}
              onCancel={() => setCreatingModel(false)}
              onSuccess={async () => {
                setCreatingModel(false)
                refetchModels()
              }}
            />
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models.map((model) => (
              <Card key={model.id}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.display_name}</span>
                        {model.is_default && (
                          <Badge className="bg-blue-100 text-blue-800 text-xs">Default</Badge>
                        )}
                        {model.enabled ? (
                          <Badge className="bg-green-100 text-green-800 text-xs">Active</Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">Disabled</Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{model.model_id}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteModel(model.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {MODEL_TYPES.find((t) => t.value === model.model_type) && (
                      <Badge variant="outline" className="text-xs">
                        {MODEL_TYPES.find((t) => t.value === model.model_type)?.label}
                      </Badge>
                    )}
                    {model.supports_images && (
                      <Badge variant="outline" className="text-xs">Images</Badge>
                    )}
                    {model.supports_video && (
                      <Badge variant="outline" className="text-xs">Video</Badge>
                    )}
                    {model.supports_audio && (
                      <Badge variant="outline" className="text-xs">Audio</Badge>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground mt-2">
                    Cost: {model.cost_per_unit} per {model.unit_type}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {models.length === 0 && (
            <Card>
              <CardContent>
                <p className="py-8 text-center text-muted-foreground">No models found</p>
              </CardContent>
            </Card>
          )}

          <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} onPageSizeChange={setPageSize} />
        </div>
      </div>
    </div>
  )
}

function ProviderForm({
  onCancel,
  onSuccess,
}: {
  onCancel: () => void
  onSuccess: () => void
}) {
  const [form, setForm] = useState({
    name: "",
    provider_type: "polza",
    base_url: "https://polza.ai/api/v1",
    api_key: "",
    enabled: true,
    priority: 0,
  })
  const [error, setError] = useState("")

  const handleSubmit = async () => {
    setError("")
    if (!form.name || !form.api_key) {
      setError("Name and API key are required")
      return
    }
    try {
      await apiFetch("/admin/ai/providers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      onSuccess()
    } catch (err: unknown) {
      setError((err as Error)?.message || "Failed to create provider")
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add Provider</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="provider-name">Name</Label>
            <Input
              id="provider-name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Polza AI"
            />
          </div>
          <div>
            <Label htmlFor="provider-type">Type</Label>
            <Select
              value={form.provider_type}
              onValueChange={(v) => setForm({ ...form, provider_type: v })}
              id="provider-type"
            >
              <option value="polza">Polza AI</option>
              <option value="openai">OpenAI</option>
              <option value="custom">Custom</option>
            </Select>
          </div>
        </div>
        <div>
          <Label htmlFor="provider-url">Base URL</Label>
          <Input
            id="provider-url"
            value={form.base_url}
            onChange={(e) => setForm({ ...form, base_url: e.target.value })}
            placeholder="https://polza.ai/api/v1"
          />
        </div>
        <div>
          <Label htmlFor="provider-key">API Key</Label>
          <Input
            id="provider-key"
            type="password"
            value={form.api_key}
            onChange={(e) => setForm({ ...form, api_key: e.target.value })}
            placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
            aria-describedby="api-key-help"
          />
          <p id="api-key-help" className="text-xs text-muted-foreground mt-1">Secret key from provider (e.g., sk-... for OpenAI)</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="provider-priority">Priority</Label>
            <Input
              id="provider-priority"
              type="number"
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: parseInt(e.target.value) || 0 })}
            />
          </div>
          <div className="flex items-end">
            <Label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.enabled}
                onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
              />
              Enabled
            </Label>
          </div>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex gap-2">
          <Button onClick={handleSubmit}>Create Provider</Button>
          <Button variant="outline" onClick={onCancel}>Cancel</Button>
        </div>
      </CardContent>
    </Card>
  )
}

function ModelForm({
  providers,
  onCancel,
  onSuccess,
}: {
  providers: AIProvider[]
  onCancel: () => void
  onSuccess: () => void
}) {
  const [form, setForm] = useState({
    provider_id: providers[0]?.id || "",
    name: "",
    display_name: "",
    model_type: "chat",
    model_id: "",
    max_prompt_length: 4096,
    supports_images: false,
    supports_video: false,
    supports_audio: false,
    cost_per_unit: 0,
    unit_type: "token",
    enabled: true,
    is_default: false,
  })
  const [error, setError] = useState("")

  const handleSubmit = async () => {
    setError("")
    if (!form.name || !form.display_name || !form.model_id || !form.provider_id) {
      setError("Name, display name, model ID, and provider are required")
      return
    }
    try {
      await apiFetch("/admin/ai/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      })
      onSuccess()
    } catch (err: unknown) {
      setError((err as Error)?.message || "Failed to create model")
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add Model</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="model-provider">Provider</Label>
            <Select
              value={form.provider_id}
              onValueChange={(v) => setForm({ ...form, provider_id: v })}
              id="model-provider"
            >
              {providers.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label htmlFor="model-type">Type</Label>
            <Select
              value={form.model_type}
              onValueChange={(v) => setForm({ ...form, model_type: v })}
              id="model-type"
            >
              {MODEL_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </Select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="model-name">Internal Name</Label>
            <Input
              id="model-name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="gpt-5-2"
            />
          </div>
          <div>
            <Label htmlFor="model-display">Display Name</Label>
            <Input
              id="model-display"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
              placeholder="ChatGPT 5.2"
            />
          </div>
        </div>
        <div>
          <Label htmlFor="model-id">Model ID (API)</Label>
          <Input
            id="model-id"
            value={form.model_id}
            onChange={(e) => setForm({ ...form, model_id: e.target.value })}
            placeholder="openai/gpt-5-2"
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <Label htmlFor="model-max-prompt">Max Prompt Length</Label>
            <Input
              id="model-max-prompt"
              type="number"
              value={form.max_prompt_length}
              onChange={(e) => setForm({ ...form, max_prompt_length: parseInt(e.target.value) || 0 })}
            />
          </div>
          <div>
            <Label htmlFor="model-cost">Cost per Unit</Label>
            <Input
              id="model-cost"
              type="number"
              step="0.001"
              value={form.cost_per_unit}
              onChange={(e) => setForm({ ...form, cost_per_unit: parseFloat(e.target.value) || 0 })}
            />
          </div>
          <div>
            <Label htmlFor="model-unit">Unit Type</Label>
            <Select
              value={form.unit_type}
              onValueChange={(v) => setForm({ ...form, unit_type: v })}
              id="model-unit"
            >
              <option value="token">Token</option>
              <option value="second">Second</option>
              <option value="image">Image</option>
              <option value="request">Request</option>
            </Select>
          </div>
        </div>
        <div className="flex flex-wrap gap-4">
          <Label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.supports_images}
              onChange={(e) => setForm({ ...form, supports_images: e.target.checked })}
            />
            Supports Images
          </Label>
          <Label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.supports_video}
              onChange={(e) => setForm({ ...form, supports_video: e.target.checked })}
            />
            Supports Video
          </Label>
          <Label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.supports_audio}
              onChange={(e) => setForm({ ...form, supports_audio: e.target.checked })}
            />
            Supports Audio
          </Label>
          <Label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.is_default}
              onChange={(e) => setForm({ ...form, is_default: e.target.checked })}
            />
            Default Model
          </Label>
          <Label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.enabled}
              onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
            />
            Enabled
          </Label>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex gap-2">
          <Button onClick={handleSubmit}>Create Model</Button>
          <Button variant="outline" onClick={onCancel}>Cancel</Button>
        </div>
      </CardContent>
    </Card>
  )
}
