import { redirect } from "next/navigation"
import { cookies } from "next/headers"

export default function HomePage() {
  const token = cookies().get("session")?.value
  if (!token) {
    redirect("/splash")
  }
  redirect("/home")
}
