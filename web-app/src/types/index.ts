export interface User {
  gender?: "male" | "female" | "teen" | "other"
  age?: number
  photos: string[]
  isOnboarded: boolean
  phone?: string
}

export interface Recipient {
  id: string
  name: string
  age?: number
  nickname?: string
  gender?: "male" | "female" | "teen" | "other"
  relationship?: string
  interests: string[]
  personality: string[]
  customNotes?: string
  photoUrl?: string
}

export type Mood = "tears" | "laugh" | "wow" | "stylish" | "cinematic" | "unusual"

export type Occasion =
  | "birthday"
  | "new_year"
  | "march_8"
  | "february_23"
  | "wedding"
  | "anniversary"
  | "graduation"
  | "defender_day"
  | "custom"

export interface Concept {
  id: string
  title: string
  description: string
  tags: string[]
}

export interface GreetingText {
  text: string
  style: string
  tone: string
}

export interface TemplateConcept {
  id: string
  title: string
  description: string
  thumbnail?: string
}

export type PaymentStatus = "pending" | "processing" | "completed" | "failed"

export interface Payment {
  amount: number
  currency: string
  method: string
  status: PaymentStatus
  bonusUsed: number
}

export type GenerationStep = "analyzing" | "scripting" | "rendering" | "compositing" | "encoding" | "finalizing"

export interface GenerationProgress {
  step: GenerationStep
  progress: number
  stepProgress: number
}

export type RatingValue = 1 | 2 | 3 | 4 | 5

export interface Greeting {
  id: string
  recipientId?: string
  recipientName?: string
  recipientAge?: number
  recipientGender?: string
  occasion: Occasion
  relationship?: string
  mood: Mood
  concepts: Concept[]
  selectedConceptId?: string
  greetingText?: GreetingText
  template?: TemplateConcept
  interests?: string[]
  personality?: string[]
  customNotes?: string
  status: "draft" | "ready" | "generating" | "completed"
  createdAt: string
  updatedAt: string
  payment?: Payment
  generation?: GenerationProgress
  rating?: RatingValue
  feedback?: string
}

export interface AppState {
  user: User
  recipients: Recipient[]
  currentGreeting: Greeting | null
  history: Greeting[]
}
