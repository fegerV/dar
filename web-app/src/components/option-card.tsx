"use client"

import { useTranslation } from "react-i18next"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface OptionCardProps {
  title: string
  description?: string
  icon?: React.ReactNode
  selected?: boolean
  onClick?: () => void
  className?: string
  children?: React.ReactNode
}

export function OptionCard({ title, description, icon, selected, onClick, className, children }: OptionCardProps) {
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
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {icon && <div className="flex-shrink-0 mt-0.5">{icon}</div>}
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base">{t(title)}</CardTitle>
            {description && <p className="text-sm text-muted-foreground mt-1">{t(description)}</p>}
            {children}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
