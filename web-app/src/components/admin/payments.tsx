"use client"

import { useTranslation } from "react-i18next"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Eye } from "lucide-react"

const payments = [
  { id: "PAY-001", user: "Иван Петров", amount: "590 ₽", provider: "YooKassa", status: "paid", date: "2026-08-18" },
  { id: "PAY-002", user: "Анна Смирнова", amount: "790 ₽", provider: "YooKassa", status: "pending", date: "2026-08-18" },
  { id: "PAY-003", user: "Алексей Кузнецов", amount: "490 ₽", provider: "YooKassa", status: "failed", date: "2026-08-17" },
  { id: "PAY-004", user: "Мария Иванова", amount: "890 ₽", provider: "YooKassa", status: "paid", date: "2026-08-17" },
]

const statusColors: Record<string, string> = {
  paid: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  failed: "bg-red-100 text-red-800",
  refunded: "bg-gray-100 text-gray-800",
}

export function AdminPayments() {
  const { t } = useTranslation()
  const [search, setSearch] = useState("")

  const filtered = payments.filter((p) => {
    if (search && !p.id.toLowerCase().includes(search.toLowerCase()) && !p.user.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Payments</h1>
        <p className="text-muted-foreground mt-1">Payments and wallet ledger</p>
      </div>

      <Card>
        <CardHeader>
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              placeholder="Search payments..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
              aria-label="Search payments"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Payments table">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">ID</th>
                  <th className="text-left py-3 px-4 font-medium">User</th>
                  <th className="text-right py-3 px-4 font-medium">Amount</th>
                  <th className="text-left py-3 px-4 font-medium">Provider</th>
                  <th className="text-center py-3 px-4 font-medium">Status</th>
                  <th className="text-left py-3 px-4 font-medium">Date</th>
                  <th className="text-right py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((payment) => (
                  <tr key={payment.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="py-3 px-4 font-mono">{payment.id}</td>
                    <td className="py-3 px-4">{payment.user}</td>
                    <td className="py-3 px-4 text-right">{payment.amount}</td>
                    <td className="py-3 px-4">{payment.provider}</td>
                    <td className="py-3 px-4 text-center">
                      <Badge className={statusColors[payment.status] || "bg-gray-100"}>{payment.status}</Badge>
                    </td>
                    <td className="py-3 px-4">{payment.date}</td>
                    <td className="py-3 px-4 text-right">
                      <Button size="sm" variant="ghost" aria-label={`View payment ${payment.id}`}>
                        <Eye className="h-4 w-4" aria-hidden="true" />
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
