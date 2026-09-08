"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Database, Cpu, Bot, HardDrive, Info, GitBranch, Book, CheckSquare, Activity, FileText, Search, AlertTriangle, Shield, Users, ShoppingCart, Cog, BarChart3, Wrench } from "lucide-react"
import { useTranslation } from "react-i18next"
import { apiFetch } from "@/lib/api"
import { useAdminAuth } from "@/contexts/admin-auth-context"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface HealthResponse {
  status: string
  database: boolean
  redis: boolean
  ai_providers: Record<string, boolean>
  storage: boolean
  disk: { total: number; used: number; free: number; used_percent: number }
  disk_alert: boolean
  queue_depth: Record<string, unknown>
  user_count: number | object
  components: Record<string, number>
}

interface DashboardStats {
  total_users: number
  total_projects: number
  total_payments: number
  pending_reviews: number
  active_generations: number
  running_jobs: number
  queued_jobs: number
  failed_jobs: number
  ai_cost_today: number
  revenue_today: number
  profit_today: number
}

interface KnowledgeSection {
  id: string
  title: string
  icon: React.ReactNode
  description: string
  color: string
}

const knowledgeSections: KnowledgeSection[] = [
  {
    id: "first-steps",
    title: "Первые шаги",
    icon: <Search className="h-5 w-5" />,
    description: "Вход в админку, настройка 2FA TOTP, RBAC роли и права доступа",
    color: "bg-blue-500"
  },
  {
    id: "structure",
    title: "Структура админки",
    icon: <Book className="h-5 w-5" />,
    description: "Навигационное меню из 24 разделов с описанием",
    color: "bg-purple-500"
  },
  {
    id: "main-sections",
    title: "Основные разделы",
    icon: <BarChart3 className="h-5 w-5" />,
    description: "Dashboard, Users, Orders, AI Providers, Workers, Ledger, Audit Logs",
    color: "bg-green-500"
  },
  {
    id: "security",
    title: "Безопасность",
    icon: <Shield className="h-5 w-5" />,
    description: "Политика паролей, CSRF защита, управление сессиями",
    color: "bg-red-500"
  },
  {
    id: "monitoring",
    title: "Мониторинг",
    icon: <Activity className="h-5 w-5" />,
    description: "System Health, Analytics, Errors — диагностика системы",
    color: "bg-orange-500"
  },
  {
    id: "common-tasks",
    title: "Частые задачи",
    icon: <Wrench className="h-5 w-5" />,
    description: "6 пошаговых инструкций для типичных операций",
    color: "bg-cyan-500"
  },
  {
    id: "emergency",
    title: "Аварийные ситуации",
    icon: <AlertTriangle className="h-5 w-5" />,
    description: "4 сценария с командами и действиями",
    color: "bg-amber-600"
  },
  {
    id: "glossary",
    title: "Глоссарий",
    icon: <FileText className="h-5 w-5" />,
    description: "14 терминов с определениями",
    color: "bg-pink-500"
  }
]

const checklistItems = [
  { period: "Первый день", items: [
    "Получить учётные данные от super_admin",
    "Войти в админку с временным паролем",
    "Сменить пароль на соответствующий политике безопасности",
    "Настроить 2FA в приложении-аутентификаторе",
    "Сохранить резервные коды 2FA в менеджере паролей",
    "Пройтись по всем 24 разделам меню для ознакомления"
  ]},
  { period: "Первая неделя", items: [
    "Изучить базу знаний",
    "Прочитать SECURITY.md и BACKUP.md",
    "Познакомиться с командой (Slack/Telegram)",
    "Получить доступ к мониторингу (Grafana/Prometheus)",
    "Научиться читать Audit Logs",
    "Потренироваться на staging-окружении"
  ]},
  { period: "Первый месяц", items: [
    "Самостоятельно обработать 5+ тикетов поддержки",
    "Оформить 2+ возврата средств",
    "Отключить/включить AI провайдера",
    "Провести экспорт данных пользователя (GDPR)",
    "Участвовать в on-call ротации (под присмотром)",
    "Пройти аттестацию на знание системы"
  ]},
  { period: "Ежеквартально", items: [
    "Сменить пароль (обязательно по политике)",
    "Перепроверить настройки 2FA",
    "Пройти refresher training по безопасности",
    "Обновить знания по новым фичам платформы"
  ]}
]

const rolesTable = [
  { role: "super_admin", level: 100, description: "Полный доступ ко всем функциям системы" },
  { role: "admin", level: 80, description: "Управление пользователями, заказами, контентом" },
  { role: "moderator", level: 60, description: "Модерация контента, работа с обращениями" },
  { role: "support", level: 40, description: "Просмотр тикетов, базовая информация о пользователях" },
  { role: "viewer", level: 20, description: "Только просмотр дашборда и статистики" }
]

const glossaryTerms = [
  { term: "RBAC", definition: "Role-Based Access Control — модель контроля доступа на основе ролей" },
  { term: "2FA/TOTP", definition: "Двухфакторная аутентификация через Time-based One-Time Password" },
  { term: "CSRF", definition: "Cross-Site Request Forgery — тип атаки, когда злоумышленник выполняет действия от имени пользователя" },
  { term: "Audit Log", definition: "Журнал аудита — запись всех значимых действий в системе" },
  { term: "Ledger", definition: "Главная книга — система бухгалтерского учёта с двойной записью" },
  { term: "Worker", definition: "Фоновый процесс, выполняющий асинхронные задачи" },
  { term: "Queue", definition: "Очередь задач — структура данных для управления фоновыми заданиями" },
  { term: "Rate Limit", definition: "Ограничение количества запросов за единицу времени" },
  { term: "API Provider", definition: "Внешний сервис, предоставляющий AI модели через API" },
  { term: "Token (AI)", definition: "Единица измерения текста для AI моделей (~¾ слова)" },
  { term: "RPM/TPM", definition: "Requests/Tokens Per Minute — лимиты запросов/токенов в минуту" },
  { term: "GDPR", definition: "General Data Protection Regulation — регламент ЕС о защите персональных данных" },
  { term: "Post-mortem", definition: "Документ с анализом инцидента после его устранения" },
  { term: "Rollback", definition: "Откат системы к предыдущей стабильной версии" }
]

const emergencyScenarios = [
  {
    title: "Database недоступна",
    severity: "critical",
    symptoms: ["Ошибки подключения к БД в логах", "Admin panel не загружается", "API возвращает 500 errors"],
    actions: [
      "Проверить статус PostgreSQL: systemctl status postgresql",
      "Проверить подключение: psql -h localhost -U daragent -d daragent_db",
      "При необходимости переключиться на реплику",
      "Восстановить из backup при повреждении данных"
    ]
  },
  {
    title: "Утечка API ключей",
    severity: "critical",
    symptoms: ["Аномальный рост расходов на AI", "Неизвестные IP адреса в логах", "Уведомления от провайдеров"],
    actions: [
      "Немедленно отозвать скомпрометированные ключи",
      "Сгенерировать новые API keys у провайдеров",
      "Проверить несанкционированную активность в логах",
      "Заблокировать скомпрометированные аккаунты"
    ]
  },
  {
    title: "DDoS атака",
    severity: "high",
    symptoms: ["Резкий рост трафика (10x-100x)", "Высокая загрузка CPU/RAM", "Таймауты запросов"],
    actions: [
      "Включить режим защиты Cloudflare: Under Attack",
      "Настроить rate limiting на уровне NGINX",
      "Заблокировать очевидные ботнеты через iptables",
      "Масштабировать инфраструктуру"
    ]
  },
  {
    title: "Критическая ошибка в production",
    severity: "high",
    symptoms: ["Массовые жалобы пользователей", "Ошибки 500 на ключевых endpoint'ах"],
    actions: [
      "Оценить масштаб через метрики и логи",
      "Выполнить rollback к предыдущей версии",
      "При невозможности — deploy hotfix",
      "Отключить проблемную фичу через feature flag"
    ]
  }
]

export default function AdminHelpPage() {
  const { t } = useTranslation()
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const { user, loading: authLoading } = useAdminAuth()
  const [selectedSection, setSelectedSection] = useState<string | null>(null)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/admin/login")
    }
  }, [authLoading, user, router])

  useEffect(() => {
    if (!user) return
    setLoading(true)
    Promise.all([
      fetch(`${process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") || "http://localhost:8000"}/health/detailed`).then(r => r.ok ? r.json() : null).catch(() => null),
      apiFetch<DashboardStats>("/admin/stats").catch(() => null),
    ]).then(([h, s]) => {
      setHealth(h)
      setStats(s)
    }).finally(() => setLoading(false))
  }, [user])

  const formatBytes = (bytes: number) => {
    const units = ["B", "KB", "MB", "GB", "TB"]
    let size = bytes
    let unitIndex = 0
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-500"
      case "high": return "bg-orange-500"
      case "medium": return "bg-yellow-500"
      default: return "bg-blue-500"
    }
  }

  if (authLoading) {
    return <p className="text-center py-8">{t("common.loading")}</p>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">{t("admin.system.help_title")}</h1>
        <p className="text-muted-foreground mt-1">Полная база знаний администратора DarAgent</p>
      </div>

      <Tabs defaultValue="knowledge" className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4">
          <TabsTrigger value="knowledge">База знаний</TabsTrigger>
          <TabsTrigger value="checklist">Чеклист</TabsTrigger>
          <TabsTrigger value="health">System Health</TabsTrigger>
          <TabsTrigger value="docs">Документация</TabsTrigger>
        </TabsList>

        <TabsContent value="knowledge" className="space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-4">Разделы базы знаний</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {knowledgeSections.map((section) => (
                <Card 
                  key={section.id} 
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => setSelectedSection(selectedSection === section.id ? null : section.id)}
                >
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{section.title}</CardTitle>
                    <div className={`p-2 rounded-full ${section.color} text-white`}>
                      {section.icon}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-muted-foreground">{section.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {selectedSection && (
            <section>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    {knowledgeSections.find(s => s.id === selectedSection)?.icon}
                    {knowledgeSections.find(s => s.id === selectedSection)?.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px] w-full rounded-md border p-4">
                    <div className="space-y-4">
                      {selectedSection === "first-steps" && (
                        <>
                          <h3 className="font-semibold">Вход в админку</h3>
                          <p className="text-sm text-muted-foreground">
                            URL входа: https://daragent.ru/admin/login
                            <br />
                            Требования: роль не ниже admin, 2FA обязательно для super_admin и admin,
                            доступ только с доверенных IP.
                          </p>
                          <h3 className="font-semibold mt-4">Настройка 2FA TOTP</h3>
                          <ol className="list-decimal list-inside text-sm text-muted-foreground space-y-1">
                            <li>Перейдите в раздел «Безопасность» профиля</li>
                            <li>Нажмите «Настроить 2FA»</li>
                            <li>Отсканируйте QR-код приложением-аутентификатором</li>
                            <li>Сохраните резервные коды восстановления</li>
                            <li>Введите 6-значный код для подтверждения</li>
                          </ol>
                          <h3 className="font-semibold mt-4">RBAC Роли</h3>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Роль</TableHead>
                                <TableHead>Уровень</TableHead>
                                <TableHead>Описание</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {rolesTable.map((role) => (
                                <TableRow key={role.role}>
                                  <TableCell className="font-medium">{role.role}</TableCell>
                                  <TableCell>{role.level}</TableCell>
                                  <TableCell>{role.description}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </>
                      )}

                      {selectedSection === "structure" && (
                        <div className="space-y-4">
                          <h3 className="font-semibold">Навигационное меню (24 раздела)</h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <h4 className="font-medium mb-2">Основная панель:</h4>
                              <ul className="list-disc list-inside text-muted-foreground space-y-1">
                                <li>Dashboard — сводная статистика</li>
                                <li>Analytics — детальные отчёты</li>
                                <li>Errors — логи ошибок</li>
                              </ul>
                            </div>
                            <div>
                              <h4 className="font-medium mb-2">Пользователи:</h4>
                              <ul className="list-disc list-inside text-muted-foreground space-y-1">
                                <li>Users — список пользователей</li>
                                <li>Roles & Permissions — роли и права</li>
                                <li>Sessions — активные сессии</li>
                              </ul>
                            </div>
                            <div>
                              <h4 className="font-medium mb-2">Контент:</h4>
                              <ul className="list-disc list-inside text-muted-foreground space-y-1">
                                <li>Projects — проекты платформы</li>
                                <li>Templates — библиотека шаблонов</li>
                                <li>Media Library — файлы и медиа</li>
                              </ul>
                            </div>
                            <div>
                              <h4 className="font-medium mb-2">Заказы:</h4>
                              <ul className="list-disc list-inside text-muted-foreground space-y-1">
                                <li>Orders — история заказов</li>
                                <li>Payments — платежи и транзакции</li>
                                <li>Ledger — финансовый учёт</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      )}

                      {selectedSection === "emergency" && (
                        <div className="space-y-4">
                          {emergencyScenarios.map((scenario, idx) => (
                            <Card key={idx} className="border-l-4 border-l-red-500">
                              <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                  <Badge className={getSeverityColor(scenario.severity)}>
                                    {scenario.severity === "critical" ? "Критический" : "Высокий"}
                                  </Badge>
                                  {scenario.title}
                                </CardTitle>
                              </CardHeader>
                              <CardContent>
                                <div className="space-y-2">
                                  <div>
                                    <h4 className="font-medium text-sm">Симптомы:</h4>
                                    <ul className="list-disc list-inside text-xs text-muted-foreground">
                                      {scenario.symptoms.map((s, i) => <li key={i}>{s}</li>)}
                                    </ul>
                                  </div>
                                  <div>
                                    <h4 className="font-medium text-sm">Действия:</h4>
                                    <ol className="list-decimal list-inside text-xs text-muted-foreground">
                                      {scenario.actions.map((a, i) => <li key={i}>{a}</li>)}
                                    </ol>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      )}

                      {selectedSection === "glossary" && (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Термин</TableHead>
                              <TableHead>Определение</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {glossaryTerms.map((item) => (
                              <TableRow key={item.term}>
                                <TableCell className="font-medium">{item.term}</TableCell>
                                <TableCell>{item.definition}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      )}

                      {(selectedSection === "main-sections" || selectedSection === "security" || selectedSection === "monitoring" || selectedSection === "common-tasks") && (
                        <p className="text-sm text-muted-foreground">
                          Подробная информация доступна в полном документе документации.
                          Откройте вкладку «Документация» для просмотра полной версии.
                        </p>
                      )}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </section>
          )}
        </TabsContent>

        <TabsContent value="checklist" className="space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-4">Чеклист нового админа</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {checklistItems.map((period, idx) => (
                <Card key={idx}>
                  <CardHeader>
                    <CardTitle className="text-lg">{period.period}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {period.items.map((item, itemIdx) => (
                        <div key={itemIdx} className="flex items-start gap-2">
                          <CheckSquare className="h-4 w-4 text-muted-foreground mt-0.5" />
                          <span className="text-sm text-muted-foreground">{item}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-4">Таблица прав доступа</h2>
            <Card>
              <CardContent className="p-0">
                <ScrollArea className="h-[400px] w-full">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="sticky top-0 bg-background z-10">Раздел</TableHead>
                        <TableHead className="sticky top-0 bg-background z-10">super_admin</TableHead>
                        <TableHead className="sticky top-0 bg-background z-10">admin</TableHead>
                        <TableHead className="sticky top-0 bg-background z-10">moderator</TableHead>
                        <TableHead className="sticky top-0 bg-background z-10">support</TableHead>
                        <TableHead className="sticky top-0 bg-background z-10">viewer</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[
                        ["Dashboard", "✅", "✅", "✅", "✅", "✅"],
                        ["Analytics", "✅", "✅", "✅", "❌", "✅"],
                        ["Errors", "✅", "✅", "✅", "❌", "❌"],
                        ["Users (view)", "✅", "✅", "✅", "✅", "❌"],
                        ["Users (edit)", "✅", "✅", "❌", "❌", "❌"],
                        ["Users (delete)", "✅", "❌", "❌", "❌", "❌"],
                        ["Roles & Permissions", "✅", "❌", "❌", "❌", "❌"],
                        ["Projects", "✅", "✅", "✅", "✅", "✅"],
                        ["Orders", "✅", "✅", "✅", "✅", "✅"],
                        ["Payments", "✅", "✅", "❌", "❌", "✅"],
                        ["Ledger", "✅", "✅", "❌", "❌", "❌"],
                        ["AI Providers", "✅", "✅", "❌", "❌", "❌"],
                        ["Workers", "✅", "✅", "❌", "❌", "❌"],
                        ["System Health", "✅", "✅", "✅", "❌", "❌"],
                        ["Settings", "✅", "✅", "❌", "❌", "❌"],
                        ["Audit Logs", "✅", "✅", "✅", "❌", "❌"],
                      ].map((row, idx) => (
                        <TableRow key={idx}>
                          <TableCell className="font-medium">{row[0]}</TableCell>
                          <TableCell className="text-center">{row[1]}</TableCell>
                          <TableCell className="text-center">{row[2]}</TableCell>
                          <TableCell className="text-center">{row[3]}</TableCell>
                          <TableCell className="text-center">{row[4]}</TableCell>
                          <TableCell className="text-center">{row[5]}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </ScrollArea>
              </CardContent>
            </Card>
          </section>
        </TabsContent>

        <TabsContent value="health" className="space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-4">{t("admin.system.help_health")}</h2>
            {loading ? (
              <p className="text-sm text-muted-foreground">{t("admin.system.health_loading")}</p>
            ) : health ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_database")}</CardTitle>
                    <Database className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{health.database ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                    <CardDescription>{health.status}</CardDescription>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Redis</CardTitle>
                    <Cpu className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{health.redis ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_ai")}</CardTitle>
                    <Bot className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {Object.values(health.ai_providers).every(Boolean) ? "✅ " + t("common.ok") : "❌ " + t("common.error")}
                    </div>
                    {Object.entries(health.ai_providers).map(([name, healthy]) => (
                      <p key={name} className="text-xs text-muted-foreground">
                        {name}: {healthy ? "✅" : "❌"}
                      </p>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_storage")}</CardTitle>
                    <HardDrive className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{health.storage ? "✅ " + t("common.ok") : "❌ " + t("common.error")}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_disk")}</CardTitle>
                    <HardDrive className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{health.disk.used_percent.toFixed(1)}%</div>
                    <CardDescription>
                      {t("admin.system.help_disk_used")}: {formatBytes(health.disk.used)} | {t("admin.system.help_disk_free")}: {formatBytes(health.disk.free)}
                    </CardDescription>
                    {health.disk_alert && (
                      <p className="text-xs text-red-500 mt-1">{t("admin.system.help_disk_alert")}</p>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_queue")}</CardTitle>
                    <GitBranch className="h-5 w-5 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{health.queue_depth ? Object.keys(health.queue_depth).length : 0}</div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">{t("admin.system.health_unavailable")}</p>
            )}
          </section>

          {stats && (
            <section>
              <h2 className="text-xl font-semibold mb-4">Key Metrics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_users")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.total_users.toLocaleString()}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_projects")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.total_projects.toLocaleString()}</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_ai_cost")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.ai_cost_today.toLocaleString()} ₽</div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">{t("admin.system.help_profit")}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.profit_today.toLocaleString()} ₽</div>
                  </CardContent>
                </Card>
              </div>
            </section>
          )}
        </TabsContent>

        <TabsContent value="docs" className="space-y-6">
          <section>
            <h2 className="text-xl font-semibold mb-4">Полная документация</h2>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Book className="h-5 w-5" />
                  База знаний администратора DarAgent
                </CardTitle>
                <CardDescription>
                  Полный документ документации доступен по ссылке ниже
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <div className="space-y-1">
                    <p className="font-medium">ADMIN_KNOWLEDGE_BASE.md</p>
                    <p className="text-sm text-muted-foreground">
                      8 разделов • 600+ строк • Версия 1.0
                    </p>
                  </div>
                  <Button variant="outline" onClick={() => window.open("/docs/ADMIN_KNOWLEDGE_BASE.md", "_blank")}>
                    <FileText className="h-4 w-4 mr-2" />
                    Открыть документ
                  </Button>
                </div>

                <div className="space-y-2 text-sm text-muted-foreground">
                  <p><strong>Содержание:</strong></p>
                  <ol className="list-decimal list-inside space-y-1">
                    <li>Первые шаги — вход, 2FA, RBAC</li>
                    <li>Структура админки — 24 раздела меню</li>
                    <li>Основные разделы — Dashboard, Users, Orders, AI Providers, Workers, Ledger, Audit Logs</li>
                    <li>Безопасность — политика паролей, CSRF, сессии</li>
                    <li>Мониторинг и диагностика — System Health, Analytics, Errors</li>
                    <li>Частые задачи — 6 пошаговых инструкций</li>
                    <li>Аварийные ситуации — 4 сценария с командами</li>
                    <li>Глоссарий — 14 терминов</li>
                  </ol>
                </div>

                <div className="pt-4 border-t">
                  <h4 className="font-medium mb-2">Приложения:</h4>
                  <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                    <li>Чеклист нового админа (14 пунктов)</li>
                    <li>Таблица прав доступа (25 разделов × 5 ролей)</li>
                    <li>Контакты поддержки (внутренние и внешние)</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </section>
        </TabsContent>
      </Tabs>

      <section>
        <h2 className="text-xl font-semibold mb-4">Quick Reference</h2>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5" />
                Полезные ссылки
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium mb-2">System Health Dashboard</h3>
                  <p className="text-sm text-muted-foreground">
                    Используйте страницу System для мониторинга состояния платформы: 
                    база данных, Redis, AI провайдеры, хранилище и диск. 
                    Красные индикаторы требуют немедленного внимания.
                  </p>
                </div>
                <div>
                  <h3 className="font-medium mb-2">Feature Flags</h3>
                  <p className="text-sm text-muted-foreground">
                    Флаги функций контролируют экспериментальную функциональность. 
                    Recommendation Engine обеспечивает персонализированные предложения шаблонов. 
                    Video Lab включает расширенные видеоэффекты (beta).
                  </p>
                </div>
                <div>
                  <h3 className="font-medium mb-2">System Settings</h3>
                  <p className="text-sm text-muted-foreground">
                    Настройки генерации контролируют умолчания AI моделей и таймауты. 
                    Платёжные настройки конфигурируют интеграцию Yookassa. 
                    Всегда устанавливайте webhook secret для production.
                  </p>
                </div>
                <div>
                  <h3 className="font-medium mb-2">Audit Logs</h3>
                  <p className="text-sm text-muted-foreground">
                    Все действия администраторов логируются здесь для compliance и troubleshooting. 
                    Логи хранятся 90 дней в горячей базе и 7 лет в архиве.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  )
}
