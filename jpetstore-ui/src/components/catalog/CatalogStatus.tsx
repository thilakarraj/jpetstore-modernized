import { Button } from "@/components/ui/Button";

export function CatalogStatus({
  loading,
  error,
  empty,
  emptyMessage = "No items to display.",
  onRetry,
}: {
  loading: boolean;
  error: string | null;
  empty?: boolean;
  emptyMessage?: string;
  onRetry?: () => void;
}) {
  if (loading) {
    return <p className="text-muted-foreground">Loading catalog…</p>;
  }
  if (error) {
    return (
      <div
        className="rounded-xl border border-error/40 bg-error/5 p-6 text-error"
        role="alert"
      >
        <p className="font-medium">Could not load catalog data</p>
        <p className="mt-2 text-sm">{error}</p>
        {onRetry ? (
          <Button type="button" variant="outline" className="mt-4" onClick={onRetry}>
            Retry
          </Button>
        ) : null}
      </div>
    );
  }
  if (empty) {
    return (
      <div className="rounded-xl border border-border bg-surface p-8 text-center text-muted-foreground">
        <p>{emptyMessage}</p>
        {onRetry ? (
          <Button type="button" variant="outline" className="mt-4" onClick={onRetry}>
            Retry
          </Button>
        ) : null}
      </div>
    );
  }
  return null;
}
