"use client";

export type ToastItem = { id: number; type: "success" | "error"; message: string };

// Deliberately not a global provider/context — each form that talks to the
// backend owns its own small toast stack (see useToasts below) rather than
// routing every fetch through one app-wide store, since the only thing that
// needs this today is surfacing otherwise-silent network failures right
// where they happen.
export function ToastStack({ toasts, onDismiss }: { toasts: ToastItem[]; onDismiss: (id: number) => void }) {
  if (toasts.length === 0) return null;

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex flex-col items-center gap-2 px-4">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="status"
          className={`pointer-events-auto flex w-full max-w-sm items-center justify-between gap-3 rounded-lg border px-4 py-3 text-[13.5px] font-semibold shadow-lg ${
            toast.type === "success"
              ? "border-green/40 bg-green/15 text-green"
              : "border-red/40 bg-red/15 text-red"
          }`}
        >
          <span>{toast.message}</span>
          <button
            type="button"
            aria-label="Zamknij"
            onClick={() => onDismiss(toast.id)}
            className="shrink-0 opacity-70 transition-opacity hover:opacity-100"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
