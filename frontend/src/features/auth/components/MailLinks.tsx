import { ExternalLink } from "lucide-react";

const GMAIL = { name: "Gmail", href: "https://mail.google.com" };
const OUTLOOK = { name: "Outlook", href: "https://outlook.office.com/mail/" };

function providersFor(email: string) {
  const domain = email.split("@")[1] ?? "";
  if (domain === "gmail.com" || domain === "googlemail.com") return [GMAIL];
  if (domain === "tha.de" || domain === "hs-augsburg.de") return [OUTLOOK];
  return [GMAIL, OUTLOOK];
}

export function MailLinks({ email }: { email: string }) {
  return (
    <div className="flex items-center justify-center gap-6">
      {providersFor(email).map((p) => (
        <a
          key={p.name}
          href={p.href}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          Open {p.name}
          <ExternalLink className="size-3.5" />
        </a>
      ))}
    </div>
  );
}
