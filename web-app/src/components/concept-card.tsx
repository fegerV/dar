"use client"

import { useTranslation } from "react-i18next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ConceptCardProps {
  concept: {
    id: string
    title: string
    description: string
    tags: string[]
  }
  selected?: boolean
  onClick?: () => void
  className?: string
}

export function ConceptCard({ concept, selected, onClick, className }: ConceptCardProps) {
  const { t } = useTranslation()

  return (
    <Card
      className={cn(
        "cursor-pointer transition-all hover:border-primary/50",
        selected && "border-primary ring-2 ring-primary/20",
        className
      )}
      onClick={onClick}
    >
      <CardHeader>
        <CardTitle className="text-lg">{t(concept.title)}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">{t(concept.description)}</p>
        <div className="flex flex-wrap gap-2">
          {concept.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {t(tag)}
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
