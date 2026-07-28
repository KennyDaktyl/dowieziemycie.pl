"use client";

import { useEffect, useState } from "react";

/** Animated odometer-style count-up, mirrors the design reference's meter. */
export function PriceMeter({ target = 149 }: { target?: number }) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setValue((current) => {
        const next = current + (Math.ceil((target - current) / 4) || 1);
        if (next >= target) {
          clearInterval(timer);
          return target;
        }
        return next;
      });
    }, 70);
    return () => clearInterval(timer);
  }, [target]);

  return (
    <div className="font-heading text-3xl font-bold text-green tabular-nums">{value} zł</div>
  );
}
