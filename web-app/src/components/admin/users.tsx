"use client"

import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Eye, Wallet } from "lucide-react"

const users = [
  { id: "18372", name: "Иван Петров", email: "ivan@example.com", orders: 17, spent: "8 420 ₽", status: "active" },
  { id: "18371", name: "Анна Смирнова", email: "anna@example.com", orders: 5, spent: "2 100 ₽", status: "active" },
  { id: "18370", name: "Алексей Кузнецов", email: "alex@example.com", orders: 23, spent: "12 300 ₽", status: "blocked" },
]

export function AdminUsers() {
  const { t } = useTranslation()
  const [search, setSearch] = useState("")

  const filtered = users.filter((u) => {
    if (search && !u.name.toLowerCase().includes(search.toLowerCase()) && !u.email.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Users</h1>
        <p className="text-muted-foreground mt-1">Manage users and segments</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
              <Input
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
                aria-label="Search users"
              />
            </div>
            <Button variant="outline">Segments</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Users table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">Name</th>
                  <th className="text-left py-3 px-4 font-medium">Email</th>
                  <th className="text-right py-3 px-4 font-medium">Orders</th>
                  <th className="text-right py-3 px-4 font-medium">Spent</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((user) => (
                  <tr key={user.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">#{user.id}</td>
                    <td className="py-3 px-4">{user.name}</td>
                    <td className="py-3 px-4">{user.email}</td>
                    <td className="py-3 px-4 text-right">{user.orders}</td>
                    <td className="py-3 px-4 text-right">{user.spent}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={user.status === "active" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                        {user.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end gap-2">
                        <Button size="sm" variant="ghost" aria-label={`View user ${user.id}`}>
                          <Eye className="h-4 w-4" aria-hidden="true" />
                        </Button>
                        <Button size="sm" variant="ghost" aria-label={`View wallet for user ${user.id}`}>
                          <Wallet className="h-4 w-4" aria-hidden="true" />
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
