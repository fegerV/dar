"use client"

import { useCallback, useState } from "react"
import { useTranslation } from "react-i18next"
import { Upload, X, Image as ImageIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface PhotoUploaderProps {
  photos: string[]
  onPhotosChange: (photos: string[]) => void
  max?: number
  min?: number
  className?: string
}

export function PhotoUploader({ photos, onPhotosChange, max = 10, min = 1, className }: PhotoUploaderProps) {
  const { t } = useTranslation()
  const [isDragging, setIsDragging] = useState(false)

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files) return
      const remaining = max - photos.length
      const toProcess = Array.from(files).slice(0, remaining)
      toProcess.forEach((file) => {
        const reader = new FileReader()
        reader.onload = () => {
          if (reader.result && typeof reader.result === "string") {
            onPhotosChange([...photos, reader.result])
          }
        }
        reader.readAsDataURL(file)
      })
    },
    [photos, onPhotosChange, max]
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      handleFiles(e.dataTransfer.files)
    },
    [handleFiles]
  )

  const removePhoto = useCallback(
    (index: number) => {
      onPhotosChange(photos.filter((_, i) => i !== index))
    },
    [photos, onPhotosChange]
  )

  return (
    <div className={cn("space-y-4", className)}>
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
          isDragging && "border-primary bg-primary/5",
          photos.length >= max && "opacity-50 cursor-not-allowed"
        )}
      >
        <input
          type="file"
          accept="image/*"
          multiple
          disabled={photos.length >= max}
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
          id="photo-upload-input"
        />
        <label htmlFor="photo-upload-input" className="cursor-pointer flex flex-col items-center gap-2">
          <Upload className="h-8 w-8 text-muted-foreground" />
          <p className="text-sm text-muted-foreground">
            {photos.length >= max
              ? `Максимум ${max} фото`
              : `Загрузите фото (${photos.length}/${max})`}
          </p>
        </label>
      </div>

      {photos.length > 0 && (
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
          {photos.map((photo, index) => (
            <div key={index} className="relative aspect-square rounded-lg overflow-hidden border">
              <img src={photo} alt={`Photo ${index + 1}`} className="w-full h-full object-cover" />
              <button
                onClick={() => removePhoto(index)}
                className="absolute top-1 right-1 bg-black/60 text-white rounded-full p-1 hover:bg-black/80"
                aria-label="Remove photo"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
          {photos.length < max && (
            <label
              htmlFor="photo-upload-input"
              className="aspect-square rounded-lg border-2 border-dashed flex flex-col items-center justify-center cursor-pointer hover:border-primary transition-colors"
            >
              <ImageIcon className="h-6 w-6 text-muted-foreground" />
              <span className="text-xs text-muted-foreground mt-1">+</span>
            </label>
          )}
        </div>
      )}
    </div>
  )
}
