"use client"

import { useTranslation } from "react-i18next"
import { X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface TagSelectorProps {
  tags: string[]
  selected: string[]
  onToggle: (tag: string) => void
  max?: number
  className?: string
}

export function TagSelector({ tags, selected, onToggle, max = 10, className }: TagSelectorProps) {
  const { t } = useTranslation()

  return (
    <div className={cn("flex flex-wrap gap-2", className)}>
      {tags.map((tag) => {
        const isSelected = selected.includes(tag)
        const isMaxed = !isSelected && selected.length >= max
        return (
          <Badge
            key={tag}
            variant={isSelected ? "default" : "outline"}
            className={cn(
              "cursor-pointer transition-colors",
              isMaxed && "opacity-50 cursor-not-allowed"
            )}
            onClick={() => !isMaxed && onToggle(tag)}
          >
            {t(tag)}
            {isSelected && <X className="h-3 w-3 ml-1" />}
          </Badge>
        )
      })}
    </div>
  )
}
