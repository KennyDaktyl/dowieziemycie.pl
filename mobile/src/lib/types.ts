export interface DriverBooking {
  id: number;
  site: string;
  customer_phone: string;
  customer_name: string;
  pickup_address: string;
  pickup_lat: string | null;
  pickup_lng: string | null;
  dropoff_address: string;
  dropoff_lat: string | null;
  dropoff_lng: string | null;
  scheduled_at: string;
  passenger_count: number;
  status: string;
  distance_km: string | null;
  price: string | null;
}
