"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function LogoutButton({ label, className }: { label: string; className?: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleLogout() {
    setLoading(true);
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } finally {
      router.push("/");
      router.refresh();
    }
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      disabled={loading}
      className={`cursor-pointer disabled:cursor-not-allowed disabled:opacity-60 ${className ?? ""}`}
    >
      {label}
    </button>
  );
}
