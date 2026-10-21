import type { ComponentProps, ReactNode } from "react"
import type { LucideIcon } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type Props = ComponentProps<typeof Input> & {
  label: string
  icon: LucideIcon
  trailing?: ReactNode
}

export function IconInput({ label, icon: Icon, trailing, id, ...props }: Props) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id} className="text-sm font-semibold">
        {label}
      </Label>
      <div className="relative">
        <Icon className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input id={id} className="h-11 pl-10 pr-10" {...props} />
        {trailing && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">{trailing}</div>
        )}
      </div>
    </div>
  )
}