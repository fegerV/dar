"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Search, Filter, Play, Eye } from "lucide-react"

const orders = [
  { id: "10482", user: "@ivan", occasion: "День Рожд.", template: "Gangster", status: "READY", amount: "590 ₽" },
  { id: "10481", user: "@anna", occasion: "Юбилей", template: "Mom", status: "GENERATING", amount: "790 ₽" },
  { id: "10480", user: "@alex", occasion: "Коллеге", template: "Office", status: "FAILED", amount: "490 ₽" },
  { id: "10479", user: "@maria", occasion: "Свадьба", template: "Romantic", status: "READY", amount: "890 ₽" },
  { id: "10478", user: "@petr", occasion: "День Рожд.", template: "Rockstar", status: "QUEUED", amount: "690 ₽" },
]

const statusColors: Record<string, string> = {
  READY: "bg-green-100 text-green-800",
  GENERATING: "bg-blue-100 text-blue-800",
  FAILED: "bg-red-100 text-red-800",
  QUEUED: "bg-yellow-100 text-yellow-800",
}

export function AdminOrders() {
  const { t } = useTranslation()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  const filtered = orders.filter((o) => {
    if (statusFilter !== "all" && o.status !== statusFilter) return false
    if (search && !o.id.includes(search) && !o.user.includes(search) && !o.template.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Orders</h1>
        <p className="text-muted-foreground mt-1">Manage customer orders</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
              <Input
                placeholder="Search orders..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
                aria-label="Search orders"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter} className="w-full sm:w-[180px]" aria-label="Filter by status">
              <option value="all">All</option>
              <option value="READY">Ready</option>
              <option value="GENERATING">Generating</option>
              <option value="FAILED">Failed</option>
              <option value="QUEUED">Queued</option>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Orders table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">User</th>
                  <th className="text-left py-3 px-4 font-medium">Occasion</th>
                  <th className="text-left py-3 px-4 font-medium">Template</th>
                  <th className="text-left py-3 px-4 font-medium">Status</th>
                  <th className="text-right py-3 px-4 font-medium">Amount</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((order) => (
                  <tr key={order.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">#{order.id}</td>
                    <td className="py-3 px-4">{order.user}</td>
                    <td className="py-3 px-4">{order.occasion}</td>
                    <td className="py-3 px-4">{order.template}</td>
                    <td className="py-3 px-4">
                      <Badge className={statusColors[order.status] || "bg-gray-100"}>{order.status}</Badge>
                    </td>
                    <td className="py-3 px-4 text-right">{order.amount}</td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end gap-2">
                        <Button size="sm" variant="ghost" aria-label={`View order ${order.id}`}>
                          <Eye className="h-4 w-4" aria-hidden="true" />
                        </Button>
                        <Button size="sm" variant="ghost" aria-label={`Play video for order ${order.id}`}>
                          <Play className="h-4 w-4" aria-hidden="true" />
                        </Button>
                      </div>
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
