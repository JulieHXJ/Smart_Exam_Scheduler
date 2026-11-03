import { ExternalLink } from "lucide-react";

const UNI_DOMAINS = ["tha.de", "hs-augsburg.de"];

export function MailLinks({ email }: { email: string }) {
  const domain = email.split("@")[1]?.toLowerCase() ?? "";
  if (!UNI_DOMAINS.includes(domain)) return null;

  return (
    <div className="flex items-center justify-center">
      <a
        href="https://outlook.office.com/mail/"
        target="_blank"
        rel="noreferrer"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
      >
        Open Outlook
        <ExternalLink className="size-3.5" />
      </a>
    </div>
  );
}
