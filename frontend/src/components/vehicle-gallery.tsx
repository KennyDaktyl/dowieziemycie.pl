"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { absoluteImageUrl } from "@/lib/images";

type GalleryImage = {
  image: string;
  thumbnail?: string;
  caption?: string;
};

export function VehicleGallery({ images, name }: { images: GalleryImage[]; name: string }) {
  const t = useTranslations("Fleet");
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const activeImage = activeIndex == null ? null : images[activeIndex];

  useEffect(() => {
    if (activeIndex == null) return;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setActiveIndex(null);
      if (event.key === "ArrowLeft") setActiveIndex((index) => (index == null ? index : (index - 1 + images.length) % images.length));
      if (event.key === "ArrowRight") setActiveIndex((index) => (index == null ? index : (index + 1) % images.length));
    }

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [activeIndex, images.length]);

  if (images.length === 0) return null;

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {images.map((photo, index) => (
          <button
            key={`${photo.image}-${index}`}
            type="button"
            onClick={() => setActiveIndex(index)}
            className="group relative aspect-[4/3] overflow-hidden rounded-[10px] border border-line bg-panel-2"
            aria-label={t("openPhoto")}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={absoluteImageUrl(photo.thumbnail || photo.image)}
              alt={photo.caption || name}
              className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-[1.03]"
            />
          </button>
        ))}
      </div>

      {activeImage && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-[80] flex items-center justify-center bg-black/80 px-4 py-6"
          onMouseDown={(event) => {
            if (event.currentTarget === event.target) setActiveIndex(null);
          }}
        >
          <div className="relative flex max-h-full w-full max-w-[1100px] flex-col gap-3">
            <button
              type="button"
              onClick={() => setActiveIndex(null)}
              className="ml-auto rounded-md border border-white/20 bg-black/35 px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-white/10"
            >
              {t("closeGallery")}
            </button>
            <div className="relative overflow-hidden rounded-[12px] bg-black">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={absoluteImageUrl(activeImage.image)}
                alt={activeImage.caption || name}
                className="max-h-[76vh] w-full object-contain"
              />
              {images.length > 1 && (
                <>
                  <button
                    type="button"
                    onClick={() => setActiveIndex((index) => (index == null ? index : (index - 1 + images.length) % images.length))}
                    className="absolute top-1/2 left-3 -translate-y-1/2 rounded-full border border-white/20 bg-black/45 px-3 py-2 text-white transition-colors hover:bg-black/70"
                    aria-label={t("previousPhoto")}
                  >
                    {"<"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveIndex((index) => (index == null ? index : (index + 1) % images.length))}
                    className="absolute top-1/2 right-3 -translate-y-1/2 rounded-full border border-white/20 bg-black/45 px-3 py-2 text-white transition-colors hover:bg-black/70"
                    aria-label={t("nextPhoto")}
                  >
                    {">"}
                  </button>
                </>
              )}
            </div>
            {activeImage.caption && <p className="text-center text-sm text-white/80">{activeImage.caption}</p>}
          </div>
        </div>
      )}
    </>
  );
}
