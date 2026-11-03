import { Check } from "lucide-react"

export function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <Check className="size-5" strokeWidth={3} />
      </div>
      <div className="leading-tight">
        <p className="text-base font-semibold">SmartExam</p>
        <p className="text-xs text-muted-foreground">Faculty of Computer Science</p>
      </div>
    </div>
  )
}