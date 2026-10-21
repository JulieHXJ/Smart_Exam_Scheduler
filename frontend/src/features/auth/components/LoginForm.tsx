import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { ArrowRight, Eye, EyeOff, Lock, Mail } from "lucide-react"
import { Button } from "@/components/ui/button"
import { IconInput } from "./IconInput"

export function LoginForm() {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    // TODO: call the backend auth endpoint
    navigate("/")
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <IconInput
        id="email"
        label="Email address"
        icon={Mail}
        type="email"
        placeholder="name@tha.de"
        autoComplete="email"
        required
      />
      <IconInput
        id="password"
        label="Password"
        icon={Lock}
        type={showPassword ? "text" : "password"}
        placeholder="Enter your password"
        autoComplete="current-password"
        required
        trailing={
          <button
            type="button"
            onClick={() => setShowPassword((v) => !v)}
            aria-label={showPassword ? "Hide password" : "Show password"}
            className="text-muted-foreground hover:text-foreground"
          >
            {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
          </button>
        }
      />
      <Button type="submit" className="h-11 w-full gap-2 whitespace-nowrap">
        Log in
        <ArrowRight className="size-4" />
      </Button>
    </form>
  )
}