import { redirect } from "next/navigation"
import { cookies } from "next/headers"
import { OnboardingScreen } from "@/components/onboarding"

export default function HomePage() {
  const token = cookies().get("session")?.value
  if (!token) {
    redirect("/onboarding")
  }
  redirect("/dashboard")
}
