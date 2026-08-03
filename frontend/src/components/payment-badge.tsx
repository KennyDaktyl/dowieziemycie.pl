export function PaymentBadge({ label, sublabel }: { label: string; sublabel: string }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-lg border border-line bg-panel2 px-3 py-2">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-[#635BFF] text-[13px] font-bold text-white">
        S
      </span>
      <div className="leading-tight">
        <div className="text-[12px] font-semibold text-text">{label}</div>
        <div className="text-[11px] text-muted">{sublabel}</div>
      </div>
    </div>
  );
}
