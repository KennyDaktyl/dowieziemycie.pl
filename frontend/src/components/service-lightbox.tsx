"use client";

import Image from "next/image";
import { useTranslations } from "next-intl";
import { useCallback, useEffect, useRef, useState } from "react";

import { absoluteImageUrl } from "@/lib/images";

import type { GalleryPhoto } from "./service-gallery";

/** Full-size photo viewer: ←/→/Esc, swipe on touch screens, focus kept
 * inside the dialog and returned to the thumbnail on close. Loaded lazily
 * by ServiceGallery on the first click. */
export default function ServiceLightbox({
  photos,
  startIndex,
  onClose,
}: {
  photos: GalleryPhoto[];
  startIndex: number;
  onClose: () => void;
}) {
  const t = useTranslations("Transport");
  const [index, setIndex] = useState(startIndex);
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const touchX = useRef<number | null>(null);
  const photo = photos[index];

  const prev = useCallback(() => setIndex((i) => (i - 1 + photos.length) % photos.length), [photos.length]);
  const next = useCallback(() => setIndex((i) => (i + 1) % photos.length), [photos.length]);

  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    document.body.style.overflow = "hidden";

    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose();
      else if (event.key === "ArrowLeft") prev();
      else if (event.key === "ArrowRight") next();
      else if (event.key === "Tab" && dialogRef.current) {
        const focusable = dialogRef.current.querySelectorAll<HTMLElement>("button");
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("keydown", handleKey);
      document.body.style.overflow = "";
      opener?.focus();
    };
  }, [onClose, prev, next]);

  const navButton =
    "absolute top-1/2 -translate-y-1/2 flex h-11 w-11 items-center justify-center rounded-full bg-black/60 text-[22px] text-white hover:bg-black/80";

  return (
    <div
      ref={dialogRef}
      role="dialog"
      aria-modal="true"
      aria-label={photo.alt}
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/90 p-4"
      onClick={(event) => event.target === event.currentTarget && onClose()}
      onTouchStart={(event) => (touchX.current = event.touches[0].clientX)}
      onTouchEnd={(event) => {
        if (touchX.current === null) return;
        const delta = event.changedTouches[0].clientX - touchX.current;
        if (Math.abs(delta) > 50) (delta > 0 ? prev : next)();
        touchX.current = null;
      }}
    >
      <button
        ref={closeRef}
        type="button"
        onClick={onClose}
        aria-label={t("galleryClose")}
        className="absolute top-4 right-4 flex h-11 w-11 items-center justify-center rounded-full bg-black/60 text-[24px] text-white hover:bg-black/80"
      >
        ×
      </button>
      <div className="relative flex max-h-[80vh] w-full max-w-[1200px] items-center justify-center">
        <Image
          key={photo.src}
          src={absoluteImageUrl(photo.src)}
          alt={photo.alt}
          width={photo.width}
          height={photo.height}
          sizes="(max-width: 1200px) 100vw, 1200px"
          loading="eager"
          className="max-h-[80vh] w-auto rounded-md object-contain"
        />
      </div>
      <div className="mt-3 text-center text-[14px] text-white/85">
        {photo.caption && <p>{photo.caption}</p>}
        <p aria-live="polite" className="mt-1 text-white/60">
          {index + 1}/{photos.length}
        </p>
      </div>
      {photos.length > 1 && (
        <>
          <button type="button" onClick={prev} aria-label={t("galleryPrev")} className={`${navButton} left-3`}>
            ‹
          </button>
          <button type="button" onClick={next} aria-label={t("galleryNext")} className={`${navButton} right-3`}>
            ›
          </button>
        </>
      )}
    </div>
  );
}
