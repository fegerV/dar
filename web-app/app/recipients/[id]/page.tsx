"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useTranslation } from "react-i18next"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAppStore } from "@/store/app-store"

export default function RecipientEditPage({ params }: { params: { id: string } }) {
  const { t } = useTranslation()
  const router = useRouter()
  const { state, updateRecipient, deleteRecipient } = useAppStore()
  const recipient = state.recipients.find((r) => r.id === params.id)

  const [name, setName] = useState(recipient?.name || "")
  const [age, setAge] = useState(recipient?.age?.toString() || "")
  const [nickname, setNickname] = useState(recipient?.nickname || "")
  const [relationship, setRelationship] = useState(recipient?.relationship || "")

  if (!recipient) {
    router.push("/profile")
    return null
  }

  const handleSave = () => {
    updateRecipient(recipient.id, { name, age: age ? Number(age) : undefined, nickname, relationship })
    router.push("/profile")
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto max-w-2xl">
        <button onClick={() => router.back()} className="flex items-center text-sm text-muted-foreground hover:text-foreground mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          {t("common.back")}
        </button>
        <h1 className="text-2xl font-bold mb-6">Редактировать получателя</h1>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Имя</Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="age">Возраст</Label>
            <Input id="age" type="number" value={age} onChange={(e) => setAge(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="nickname">Прозвище</Label>
            <Input id="nickname" value={nickname} onChange={(e) => setNickname(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="relationship">Отношения</Label>
            <Input id="relationship" value={relationship} onChange={(e) => setRelationship(e.target.value)} />
          </div>

          <div className="flex gap-3 pt-4">
            <Button variant="destructive" onClick={() => { deleteRecipient(recipient.id); router.push("/profile") }}>
              Удалить
            </Button>
            <Button onClick={handleSave} className="flex-1">
              Сохранить
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
