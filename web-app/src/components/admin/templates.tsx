"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Plus, Edit } from "lucide-react"

const templates = [
  { id: "1", code: "GANGSTER_BDAY", title: "Gangster Birthday", status: "published", category: "Brutal", price: "790 ₽" },
  { id: "2", code: "MOM_WARM", title: "Warm Mom", status: "published", category: "Emotional", price: "590 ₽" },
  { id: "3", code: "OFFICE_COL", title: "Office Colleague", status: "draft", category: "Professional", price: "490 ₽" },
  { id: "4", code: "ROCKSTAR", title: "Rockstar", status: "published", category: "Fun", price: "690 ₽" },
]

export function AdminTemplates() {
  const { t } = useTranslation()
  const [search, setSearch] = useState("")

  const filtered = templates.filter((tmpl) => {
    if (search && !tmpl.title.toLowerCase().includes(search.toLowerCase()) && !tmpl.code.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Templates</h1>
          <p className="text-muted-foreground mt-1">Manage template library and scenes</p>
        </div>
        <Button aria-label="Create new template">
          <Plus className="h-4 w-4 mr-2" aria-hidden="true" />
          New Template
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Search templates..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
              aria-label="Search templates"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Templates table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Code</th>
                  <th className="text-left py-3 px-4 font-medium">Title</th>
                  <th className="text-left py-3 px-4 font-medium">Category</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-right py-3 px-4 font-medium">Price</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((tmpl) => (
                  <tr key={tmpl.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">{tmpl.code}</td>
                    <td className="py-3 px-4">{tmpl.title}</td>
                    <td className="py-3 px-4">{tmpl.category}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={tmpl.status === "published" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                        {tmpl.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-right">{tmpl.price}</td>
                    <td className="py-3 px-4 text-right">
                      <Button size="sm" variant="ghost" aria-label={`Edit template ${tmpl.id}`}>
                        <Edit className="h-4 w-4" aria-hidden="true" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
