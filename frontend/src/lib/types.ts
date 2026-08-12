export interface HomeContent {
  eyebrow_pl: string;
  eyebrow_en: string;
  headline_pl: string;
  headline_en: string;
  headline_highlight_pl: string;
  headline_highlight_en: string;
  lead_pl: string;
  lead_en: string;
  footnote_pl: string;
  footnote_en: string;
  about_pl: string;
  about_en: string;
}

export interface VehiclePhotoItem {
  image: string;
  thumbnail: string;
  caption: string;
  order: number;
}

export interface Vehicle {
  id: number;
  name: string;
  model: string;
  seats: number;
  description_pl: string;
  description_en: string;
  description_de: string;
  cover_photo: string | null;
  photos: VehiclePhotoItem[];
}

export interface PricingTier {
  id: number;
  max_distance_km: number;
  price_reserved: string;
  price_on_demand: string;
}

export interface LocalFarePolicy {
  minimum_fare: string;
  included_km: number;
  local_max_distance_km: number;
  price_per_km: string;
  proximity_threshold_km: string;
}

export interface RouteEstimate {
  distance_km: number;
  duration_min: number;
  geometry: [number, number][];
  is_reserved: boolean;
  price: number | null;
  pricing_mode: "tier" | "local";
}

export interface DriverEtaLeg {
  leg_type: "direct_to_pickup" | "to_current_dropoff" | "dropoff_to_new_pickup";
  distance_km: number;
  duration_min: number;
}

export interface DriverEta {
  available: boolean;
  driver_status?: "OFFLINE" | "DOSTEPNY" | "JADACY_PO_KLIENTA" | "W_KURSIE" | "WRACA_DO_BAZY";
  basis?: "live" | "base";
  eta_minutes?: number;
  legs?: DriverEtaLeg[];
}

export interface TourPhoto {
  image: string;
  caption: string;
  order: number;
}

export interface Tour {
  slug: string;
  title_pl: string;
  title_en: string;
  summary_pl: string;
  summary_en: string;
  body_pl: string;
  body_en: string;
  price_from: string;
  cover_image: string | null;
  seo_title_pl: string;
  seo_title_en: string;
  seo_description_pl: string;
  seo_description_en: string;
  photos: TourPhoto[];
  order: number;
}

export interface LocalRoute {
  slug: string;
  destination_town: string;
  destination_lat: string;
  destination_lng: string;
  title_pl: string;
  title_en: string;
  lead_pl: string;
  lead_en: string;
  body_pl: string;
  body_en: string;
  seo_title_pl: string;
  seo_title_en: string;
  seo_description_pl: string;
  seo_description_en: string;
  example_distance_km: number;
  example_price: number | null;
  order: number;
}

export interface ContentPage {
  slug: string;
  page_type: string;
  title_pl: string;
  title_en: string;
  body_pl: string;
  body_en: string;
  seo_title_pl: string;
  seo_title_en: string;
  seo_description_pl: string;
  seo_description_en: string;
}

export interface EventOfferPhoto {
  image: string;
  thumbnail: string;
  caption: string;
  order: number;
}

export interface EventOfferListItem {
  slug: string;
  icon: string;
  cover_image: string | null;
  title_pl: string;
  title_en: string;
  excerpt_pl: string;
  excerpt_en: string;
  price_from: string | null;
}

export interface EventOffer extends EventOfferListItem {
  h1_pl: string;
  h1_en: string;
  body_pl: string;
  body_en: string;
  seo_title_pl: string;
  seo_title_en: string;
  seo_description_pl: string;
  seo_description_en: string;
  photos: EventOfferPhoto[];
}

export interface BlogPostPhoto {
  image: string;
  thumbnail: string;
  caption: string;
  order: number;
}

export interface BlogPostLink {
  label_pl: string;
  label_en: string;
  url: string;
  order: number;
}

export interface BlogPost {
  slug: string;
  tag_pl: string;
  tag_en: string;
  title_pl: string;
  title_en: string;
  excerpt_pl: string;
  excerpt_en: string;
  body_pl: string;
  body_en: string;
  cover_image: string | null;
  youtube_url: string;
  photos: BlogPostPhoto[];
  links: BlogPostLink[];
  seo_title_pl: string;
  seo_title_en: string;
  seo_description_pl: string;
  seo_description_en: string;
  published_at: string;
}

export interface DriverLiveStatus {
  id: number;
  name: string;
  status: "OFFLINE" | "DOSTEPNY" | "JADACY_PO_KLIENTA" | "W_KURSIE" | "WRACA_DO_BAZY";
  current_lat: string | null;
  current_lng: string | null;
  location_updated_at: string | null;
  vehicle_name: string | null;
  vehicle_plate: string | null;
}

export interface Customer {
  id: number;
  phone: string;
  name: string;
  created_at: string;
}

export type BookingStatus =
  | "NOWA"
  | "POTWIERDZONA"
  | "OPLACONA"
  | "KIEROWCA_W_DRODZE"
  | "W_TRAKCIE"
  | "ZAKONCZONA"
  | "ANULOWANA";

export interface Booking {
  id: number;
  pickup_address: string;
  pickup_lat: string | null;
  pickup_lng: string | null;
  dropoff_address: string;
  dropoff_lat: string | null;
  dropoff_lng: string | null;
  flight_number: string;
  scheduled_at: string;
  status: BookingStatus;
  distance_km: string | null;
  duration_minutes: number | null;
  is_reserved: boolean;
  price: string | null;
  coupon_code: string | null;
  driver_name: string | null;
  driver_vehicle: string | null;
  driver_vehicle_plate: string | null;
  driver_vehicle_seats: number | null;
  created_at: string;
  confirmed_at: string | null;
  payment_deadline: string | null;
  deposit_amount: string | null;
  paid_at: string | null;
  remainder_paid_at: string | null;
  remaining_amount: string | null;
}

export interface BookingInput {
  pickup_address: string;
  pickup_lat?: number;
  pickup_lng?: number;
  dropoff_address: string;
  dropoff_lat?: number;
  dropoff_lng?: number;
  scheduled_at: string;
  passenger_count?: number;
  coupon_code?: string;
}
