"use client";

import { useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";

import { Link } from "@/i18n/navigation";
import type { AppLocale } from "@/i18n/routing";
import { trackEvent } from "@/lib/analytics";
import { publicApiBaseUrl, withSiteHeader } from "@/lib/api";
import type { InquiryItemType } from "@/lib/types";

export const VEHICLE_OPTION_EVENT = "transport-vehicle-option";
export type VehicleOption = "bus" | "trailer" | "unknown";

const ITEM_TYPES: InquiryItemType[] = ["meble", "kartony", "agd", "rowery", "przeprowadzka", "quad-motocykl", "inne"];
const MAX_PHOTOS = 5;
const MAX_SIDE = 1600;
const UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign"] as const;
const UTM_STORAGE_KEY = "dwm_utm";

type Photo = { file: File; preview: string };
type Status = "idle" | "sending" | "success" | "error";

/** Downscales a photo to at most 1600 px and re-encodes it as JPEG, so five
 * phone photos upload in seconds instead of tens of MB. A file the browser
 * can't decode (e.g. HEIC outside Safari) is rejected rather than sent. */
async function compressPhoto(file: File): Promise<File> {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise<HTMLImageElement>((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = reject;
      image.src = url;
    });
    const scale = Math.min(1, MAX_SIDE / Math.max(img.naturalWidth, img.naturalHeight));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(img.naturalWidth * scale);
    canvas.height = Math.round(img.naturalHeight * scale);
    canvas.getContext("2d")?.drawImage(img, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.82));
    if (!blob) throw new Error("encode failed");
    return new File([blob], file.name.replace(/\.[^.]+$/, "") + ".jpg", { type: "image/jpeg" });
  } finally {
    URL.revokeObjectURL(url);
  }
}

function readUtm(): Record<string, string> {
  const fromUrl: Record<string, string> = {};
  try {
    const params = new URLSearchParams(window.location.search);
    for (const key of UTM_KEYS) {
      const value = params.get(key);
      if (value) fromUrl[key] = value.slice(0, 100);
    }
    if (Object.keys(fromUrl).length > 0) {
      sessionStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(fromUrl));
      return fromUrl;
    }
    return JSON.parse(sessionStorage.getItem(UTM_STORAGE_KEY) ?? "{}") as Record<string, string>;
  } catch {
    return fromUrl;
  }
}

export function TransportInquiryForm({
  pageSlug,
  locale,
  defaultItemType,
  phone,
}: {
  pageSlug: string;
  locale: AppLocale;
  defaultItemType: InquiryItemType | "";
  phone: string;
}) {
  const t = useTranslations("TransportForm");
  const formRef = useRef<HTMLFormElement>(null);
  const [vehicleOption, setVehicleOption] = useState<VehicleOption>("unknown");
  const [itemType, setItemType] = useState<InquiryItemType>(defaultItemType || "meble");
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [photoError, setPhotoError] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    readUtm(); // remember this visit's UTM tags for the rest of the session
    // Pricing cards ("Busem" / "Z przyczepą") preselect the option.
    function handleOption(event: Event) {
      const option = (event as CustomEvent<VehicleOption>).detail;
      setVehicleOption(option);
      formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    window.addEventListener(VEHICLE_OPTION_EVENT, handleOption);
    return () => window.removeEventListener(VEHICLE_OPTION_EVENT, handleOption);
  }, []);

  useEffect(() => () => photos.forEach((photo) => URL.revokeObjectURL(photo.preview)), [photos]);

  async function handleFiles(fileList: FileList | null) {
    if (!fileList) return;
    setPhotoError("");
    const room = MAX_PHOTOS - photos.length;
    const chosen = Array.from(fileList).slice(0, room);
    if (fileList.length > room) setPhotoError(t("photosLimit", { max: MAX_PHOTOS }));
    const added: Photo[] = [];
    for (const file of chosen) {
      try {
        const compressed = await compressPhoto(file);
        added.push({ file: compressed, preview: URL.createObjectURL(compressed) });
      } catch {
        setPhotoError(t("photoUnreadable", { name: file.name }));
      }
    }
    setPhotos((current) => [...current, ...added]);
  }

  function removePhoto(index: number) {
    setPhotos((current) => current.filter((_, i) => i !== index));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    data.delete("photos_input");
    data.set("vehicle_option", vehicleOption);
    data.set("item_type", itemType);
    data.set("needs_carrying", data.get("needs_carrying") ? "true" : "false");
    data.set("consent", data.get("consent") ? "true" : "false");
    data.set("source_page", pageSlug);
    data.set("locale", locale);
    for (const [key, value] of Object.entries(readUtm())) data.set(key, value);
    for (const photo of photos) data.append("photos", photo.file);

    setStatus("sending");
    setErrors({});
    try {
      const res = await fetch(`${publicApiBaseUrl()}/api/transport-inquiries/`, {
        method: "POST",
        body: data,
        headers: withSiteHeader(),
      });
      if (res.ok) {
        setStatus("success");
        trackEvent("generate_lead", {
          category: "transport_rzeczy",
          vehicle_option: vehicleOption,
          item_type: itemType,
          page_slug: pageSlug,
        });
        return;
      }
      if (res.status === 429) {
        setErrors({ form: t("errorThrottled") });
      } else {
        const body = (await res.json().catch(() => ({}))) as Record<string, string[] | string>;
        const fieldErrors: Record<string, string> = {};
        for (const [field, messages] of Object.entries(body)) {
          fieldErrors[field] = Array.isArray(messages) ? messages.join(" ") : String(messages);
        }
        setErrors(Object.keys(fieldErrors).length ? fieldErrors : { form: t("errorGeneric") });
      }
      setStatus("error");
    } catch {
      setErrors({ form: t("errorNetwork") });
      setStatus("error");
    }
  }

  const whatsappHref = `https://wa.me/${phone.replace(/\D/g, "")}`;

  if (status === "success") {
    return (
      <div role="status" className="rounded-xl border border-green/40 bg-panel p-6">
        <h3 className="font-heading text-[20px] font-semibold">{t("successTitle")}</h3>
        <p className="mt-2 text-[14.5px] leading-relaxed text-muted">{t("successBody")}</p>
        <p className="mt-3 text-[14.5px]">
          {t("successAlt")}{" "}
          <a href={`tel:${phone}`} className="font-semibold text-amber hover:underline">
            {phone}
          </a>{" "}
          ·{" "}
          <a href={whatsappHref} target="_blank" rel="noopener noreferrer" className="font-semibold text-amber hover:underline">
            WhatsApp
          </a>
        </p>
      </div>
    );
  }

  const input =
    "w-full rounded-md border border-line bg-bg px-3 py-2.5 text-[14.5px] text-text outline-none transition-colors focus:border-amber";
  const label = "mb-1.5 block text-[13px] font-semibold text-text";
  const fieldError = (name: string) =>
    errors[name] ? (
      <p id={`${name}-error`} className="mt-1 text-[12.5px] text-red-400">
        {errors[name]}
      </p>
    ) : null;

  return (
    <form ref={formRef} onSubmit={handleSubmit} noValidate={false} className="scroll-mt-28 grid gap-4 sm:grid-cols-2">
      {/* Honeypot — invisible to people, tempting to bots. */}
      <div aria-hidden className="absolute -left-[9999px] h-0 w-0 overflow-hidden">
        <label>
          Website
          <input type="text" name="website" tabIndex={-1} autoComplete="off" />
        </label>
      </div>

      <fieldset className="sm:col-span-2">
        <legend className={label}>{t("vehicleOption")}</legend>
        <div className="flex flex-wrap gap-2">
          {(["bus", "trailer", "unknown"] as VehicleOption[]).map((option) => (
            <label
              key={option}
              className={`cursor-pointer rounded-md border px-4 py-2 text-[14px] transition-colors ${
                vehicleOption === option ? "border-amber bg-amber/10 text-text" : "border-line text-muted hover:text-text"
              }`}
            >
              <input
                type="radio"
                name="vehicle_option_choice"
                value={option}
                checked={vehicleOption === option}
                onChange={() => setVehicleOption(option)}
                className="sr-only"
              />
              {t(`vehicle_${option}`)}
            </label>
          ))}
        </div>
        {vehicleOption === "trailer" && <p className="mt-2 text-[13px] text-muted">{t("trailerNote")}</p>}
      </fieldset>

      <div>
        <label htmlFor="ti-item-type" className={label}>
          {t("itemType")}
        </label>
        <select
          id="ti-item-type"
          value={itemType}
          onChange={(e) => setItemType(e.target.value as InquiryItemType)}
          className={input}
        >
          {ITEM_TYPES.map((type) => (
            <option key={type} value={type}>
              {t(`item_${type}`)}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="ti-date" className={label}>
          {t("preferredDate")}
        </label>
        <input id="ti-date" name="preferred_date" type="date" className={input} aria-describedby="preferred_date-error" />
        {fieldError("preferred_date")}
      </div>

      <div className="sm:col-span-2">
        <label htmlFor="ti-description" className={label}>
          {t("description")}
        </label>
        <textarea
          id="ti-description"
          name="description"
          required
          maxLength={3000}
          rows={4}
          placeholder={t("descriptionPlaceholder")}
          className={input}
          aria-describedby="description-error"
        />
        {fieldError("description")}
      </div>

      <div>
        <label htmlFor="ti-pickup" className={label}>
          {t("pickup")}
        </label>
        <input id="ti-pickup" name="pickup_address" required maxLength={255} className={input} autoComplete="street-address" />
        {fieldError("pickup_address")}
      </div>
      <div>
        <label htmlFor="ti-dropoff" className={label}>
          {t("dropoff")}
        </label>
        <input id="ti-dropoff" name="dropoff_address" required maxLength={255} className={input} />
        {fieldError("dropoff_address")}
      </div>

      <div className="sm:col-span-2">
        <span className={label}>{t("photos", { max: MAX_PHOTOS })}</span>
        <p className="mb-2 text-[12.5px] text-muted">{t("photosHint")}</p>
        <div className="flex flex-wrap gap-3">
          {photos.map((photo, index) => (
            <div key={photo.preview} className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element -- local object URL preview */}
              <img src={photo.preview} alt="" className="h-20 w-20 rounded-md object-cover" />
              <button
                type="button"
                onClick={() => removePhoto(index)}
                aria-label={t("removePhoto")}
                className="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-bg text-[13px] text-text ring-1 ring-line"
              >
                ×
              </button>
            </div>
          ))}
          {photos.length < MAX_PHOTOS && (
            <label className="flex h-20 w-20 cursor-pointer items-center justify-center rounded-md border border-dashed border-line text-[26px] text-muted hover:border-amber hover:text-amber">
              +
              <input
                type="file"
                name="photos_input"
                accept="image/jpeg,image/png,image/webp,image/heic"
                multiple
                className="sr-only"
                aria-label={t("addPhotos")}
                onChange={(e) => {
                  void handleFiles(e.target.files);
                  e.target.value = "";
                }}
              />
            </label>
          )}
        </div>
        {(photoError || errors.photos) && <p className="mt-1 text-[12.5px] text-red-400">{photoError || errors.photos}</p>}
      </div>

      <div>
        <label htmlFor="ti-name" className={label}>
          {t("name")}
        </label>
        <input id="ti-name" name="name" required maxLength={120} className={input} autoComplete="name" />
        {fieldError("name")}
      </div>
      <div>
        <label htmlFor="ti-phone" className={label}>
          {t("phone")}
        </label>
        <input id="ti-phone" name="phone" type="tel" required maxLength={32} className={input} autoComplete="tel" />
        {fieldError("phone")}
      </div>
      <div className="sm:col-span-2">
        <label htmlFor="ti-email" className={label}>
          {t("email")}
        </label>
        <input id="ti-email" name="email" type="email" maxLength={254} className={input} autoComplete="email" />
        {fieldError("email")}
      </div>

      <label className="flex items-start gap-2.5 text-[14px] sm:col-span-2">
        <input type="checkbox" name="needs_carrying" className="mt-1 accent-amber" />
        {t("needsCarrying")}
      </label>

      <div className="sm:col-span-2">
        <label className="flex items-start gap-2.5 text-[13px] leading-relaxed text-muted">
          <input type="checkbox" name="consent" required className="mt-1 accent-amber" />
          <span>
            {t.rich("consent", {
              terms: (chunks) => (
                <Link href="/regulamin" className="text-amber underline underline-offset-2">
                  {chunks}
                </Link>
              ),
            })}
          </span>
        </label>
        {fieldError("consent")}
      </div>

      {errors.form && (
        <p role="alert" className="text-[13.5px] text-red-400 sm:col-span-2">
          {errors.form}
        </p>
      )}

      <div className="flex flex-wrap items-center gap-4 sm:col-span-2">
        <button
          type="submit"
          disabled={status === "sending"}
          className="rounded-md bg-amber px-6 py-3 text-[15px] font-semibold text-[#1a1305] transition-all hover:-translate-y-px disabled:opacity-60"
        >
          {status === "sending" ? t("sending") : t("submit")}
        </button>
        <span className="text-[13px] text-muted">{t("responseNote")}</span>
      </div>
    </form>
  );
}
