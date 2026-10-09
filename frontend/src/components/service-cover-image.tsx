"use client";

import dynamic from "next/dynamic";
import Image from "next/image";
import { useState } from "react";

import { absoluteImageUrl } from "@/lib/images";

import type { GalleryPhoto } from "./service-gallery";

const ServiceLightbox = dynamic(() => import("./service-lightbox"), { ssr: false });

/** The page's main photo, shown whole at its own aspect ratio (it can be an
 * infographic — cropping would cut the text off) and clickable into the
 * full-screen lightbox. Width/height from the API reserve the space, so no
 * layout shift; it's the LCP image, hence eager + high priority. */
export function ServiceCoverImage({ photo, openLabel }: { photo: GalleryPhoto; openLabel: string }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={`${openLabel}: ${photo.alt}`}
        className="mt-8 block w-full cursor-zoom-in overflow-hidden rounded-[14px] ring-amber focus-visible:ring-2"
      >
        <Image
          src={absoluteImageUrl(photo.src)}
          alt={photo.alt}
          width={photo.width}
          height={photo.height}
          sizes="(max-width: 1408px) 100vw, 1360px"
          loading="eager"
          fetchPriority="high"
          className="h-auto w-full"
        />
      </button>
      {open && <ServiceLightbox photos={[photo]} startIndex={0} onClose={() => setOpen(false)} />}
    </>
  );
}
