import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

function Select({ value, onValueChange, children, className, ...props }: React.SelectHTMLAttributes<HTMLSelectElement> & { value?: string; onValueChange?: (value: string) => void }) {
  return (
    <div className="relative">
      <select
        value={value}
        onChange={(e) => onValueChange?.(e.target.value)}
        className={cn("flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none", className)}
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none" aria-hidden="true" />
    </div>
  )
}

export { Select }
