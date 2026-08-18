"use client"

import { useState } from "react"
import { Star } from "lucide-react"
import { cn } from "@/lib/utils"

interface RatingProps {
  value?: number
  onChange?: (value: number) => void
  size?: number
  className?: string
}

export function Rating({ value = 0, onChange, size = 28, className }: RatingProps) {
  const [hover, setHover] = useState(0)

  return (
    <div className={cn("flex items-center gap-1", className)}>
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => onChange?.(star as 1 | 2 | 3 | 4 | 5)}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(0)}
          className="p-0 bg-transparent border-none cursor-pointer"
          aria-label={`Rate ${star} star${star > 1 ? "s" : ""}`}
        >
          <Star
            className="transition-colors"
            style={{ width: size, height: size }}
            fill={(hover || value) >= star ? "currentColor" : "none"}
            color={(hover || value) >= star ? "#fbbf24" : "#d1d5db"}
          />
        </button>
      ))}
    </div>
  )
}
