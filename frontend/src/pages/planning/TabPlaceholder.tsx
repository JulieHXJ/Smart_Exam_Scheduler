export function TabPlaceholder({ name }: { name: string }) {
  return (
    <div className="rounded-xl border border-dashed bg-card p-12 text-center text-sm text-muted-foreground">
      {name} will appear here.
    </div>
  );
}
