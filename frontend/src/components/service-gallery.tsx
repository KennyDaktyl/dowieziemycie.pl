"use client";

import dynamic from "next/dynamic";
import Image from "next/image";
import { useState } from "react";

import { absoluteImageUrl } from "@/lib/images";

// Downloaded on the first click only — the grid itself ships no lightbox JS.
const ServiceLightbox = dynamic(() => import("./service-lightbox"), { ssr: false });

export type GalleryPhoto = {
  src: string;
  thumbnailSrc: string;
  width: number;
  height: number;
  alt: string;
  caption: string;
};

export function ServiceGallery({ photos, openLabel }: { photos: GalleryPhoto[]; openLabel: string }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  if (photos.length === 0) return null;

  return (
    <>
      <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {photos.map((photo, index) => (
          <li key={photo.src}>
            <button
              type="button"
              onClick={() => setOpenIndex(index)}
              aria-label={`${openLabel}: ${photo.alt}`}
              className="block w-full overflow-hidden rounded-lg bg-panel ring-amber focus-visible:ring-2"
            >
              <Image
                src={absoluteImageUrl(photo.thumbnailSrc)}
                alt={photo.alt}
                width={photo.width}
                height={photo.height}
                sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 340px"
                loading="lazy"
                className="aspect-[4/3] w-full object-cover transition-transform hover:scale-[1.03]"
              />
            </button>
          </li>
        ))}
      </ul>
      {openIndex !== null && (
        <ServiceLightbox photos={photos} startIndex={openIndex} onClose={() => setOpenIndex(null)} />
      )}
    </>
  );
}
