export interface AdminUser {
  id: string
  status: string
  email: string | null
  display_name: string | null
  is_admin: boolean
  phone: string | null
  locale: string | null
  last_seen_at: string | null
  created_at: string
}

export interface AdminTemplate {
  id: string
  code: string
  title: string
  description: string | null
  kind: string
  status: string
  category: string | null
  occasion_codes: string[]
  relationship_types: string[]
  moods: string[]
  tags: string[]
  base_price_rub: number
  cost_price_rub: number
  estimated_duration_sec: number | null
  difficulty: number | null
  personalization_score: number | null
  sort_order: number
  success_rate: number | null
  avg_rating: number | null
  usage_count: number
  completion_rate: number | null
  created_at: string
}

export interface AdminTemplateCreate {
  code: string
  title: string
  description?: string | null
  kind: string
  category?: string | null
  occasion_codes: string[]
  relationship_types: string[]
  moods: string[]
  tags: string[]
  base_price_rub: number
  cost_price_rub?: number
  estimated_duration_sec?: number | null
  difficulty?: number | null
  personalization_score?: number | null
}

export interface AdminGeneration {
  id: string
  project_id: string
  status: string
  progress: number
  current_step: string | null
  model_name: string | null
  attempt: number
  error_code: string | null
  error_message: string | null
  cost_rub: number
  duration_ms: number | null
  created_at: string
  completed_at: string | null
}

export interface AdminOrder {
  id: string
  project_id: string
  requested_by_user_id: string | null
  status: string
  cost_rub: number
  template_version_id: string | null
  model_name: string | null
  error_code: string | null
  created_at: string
  completed_at: string | null
  input_json?: Record<string, unknown> | null
  output_json?: Record<string, unknown> | null
}

export interface AdminWorker {
  id: string
  name: string
  status: string
  gpu_model: string | null
  gpu_vram_total_gb: number | null
  gpu_vram_used_gb: number | null
  cpu_usage_percent: number | null
  jobs_today: number
  failures_today: number
  avg_generation_time_sec: number | null
  last_heartbeat_at: string | null
  created_at: string
}

export interface AdminQueueJob {
  id: string
  generation_id: string
  worker_id: string | null
  status: string
  priority: number
  error_code: string | null
  error_message: string | null
  retry_count: number
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface AdminPayment {
  id: string
  user_id: string | null
  amount_rub: number
  method: string
  status: string
  provider_id: string | null
  external_payment_id: string | null
  created_at: string
  paid_at: string | null
}

export interface AdminLedgerTransaction {
  id: string
  user_id: string
  user_email: string | null
  wallet_id: string | null
  type: string
  amount_rub: number
  is_bonus: boolean
  admin_id: string | null
  reason: string
  reference_id: string | null
  created_at: string
}

export interface AdminLedgerResponse {
  transactions: AdminLedgerTransaction[]
  total: number
  page: number
  page_size: number
}

export interface AuditLog {
  id: string
  actor_user_id: string | null
  action: string
  target_type: string | null
  target_id: string | null
  ip_address: string | null
  user_agent: string | null
  created_at: string
}

export interface SystemSetting {
  id: string
  key: string
  value: Record<string, unknown>
  description: string | null
  is_public: boolean
  updated_at: string
}

export interface DashboardStats {
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

export interface UserWallet {
  user_id: string
  balance_rub: number
  bonus_balance: number
  updated_at: string | null
}

export interface ReferralCode {
  id: string
  code: string
  is_active: boolean
  uses_count: number
  max_uses: number | null
  created_at: string
}

export interface Referral {
  id: string
  code: string
  status: string
  referrer_user_id: string
  referred_user_id: string | null
  referrer_bonus_granted: boolean
  referee_bonus_granted: boolean
  metadata: Record<string, unknown> | null
  created_at: string
}


export interface AdminRole {
  id: string
  code: string
  name: string
  description: string | null
  permissions: string[]
  is_system: boolean
  created_at: string
}


export interface SystemRoleDef {
  name: string
  description: string
  permissions: string[]
}
