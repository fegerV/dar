import { AdminSidebar } from "@/components/admin/sidebar"
import { AdminAuthProvider } from "@/contexts/admin-auth-context"

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AdminAuthProvider>
      <div className="min-h-screen bg-muted/30">
        <div className="flex">
          <AdminSidebar />
          <main className="flex-1 p-6 lg:p-8">
            <div className="mx-auto max-w-7xl">
              {children}
            </div>
          </main>
        </div>
      </div>
    </AdminAuthProvider>
  )
}
