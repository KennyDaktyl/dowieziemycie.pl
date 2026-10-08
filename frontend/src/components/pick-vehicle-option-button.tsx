"use client";

import { VEHICLE_OPTION_EVENT, type VehicleOption } from "./transport-inquiry-form";

/** A pricing card's CTA: preselects its option in the inquiry form and
 * scrolls to it (the form listens for this event). */
export function PickVehicleOptionButton({ option, label }: { option: VehicleOption; label: string }) {
  return (
    <a
      href="#zapytanie"
      onClick={(event) => {
        event.preventDefault();
        window.dispatchEvent(new CustomEvent(VEHICLE_OPTION_EVENT, { detail: option }));
      }}
      className="mt-5 inline-block rounded-md border border-amber px-5 py-2.5 text-[14px] font-semibold text-amber transition-colors hover:bg-amber/10"
    >
      {label}
    </a>
  );
}
