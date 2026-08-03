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
  deposit_amount: string | null;
  confirmed_at: string | null;
  payment_deadline: string | null;
  paid_at: string | null;
  created_at: string;
  tracking_code: string;
  tracking_code_valid_from: string | null;
  tracking_code_expires_at: string | null;
  assigned_driver_id: number | null;
  assigned_driver_name: string | null;
}
