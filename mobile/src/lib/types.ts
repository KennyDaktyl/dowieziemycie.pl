export type Currency = "pln" | "eur";

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
  flight_number: string;
  scheduled_at: string;
  passenger_count: number;
  status: string;
  distance_km: string | null;
  actual_distance_km: number | null;
  duration_minutes: number | null;
  price: string | null;
  price_eur: string | null;
  deposit_amount: string | null;
  /** EUR deposit — the one set on the booking or the default rule's value. */
  deposit_amount_eur: string | null;
  /** Amounts fixed by hand for the end of the ride (null = price − deposit). */
  remainder_amount: string | null;
  remainder_amount_eur: string | null;
  /** Still unpaid balance, in each currency (null = nothing owed / unknown). */
  remaining_amount: string | null;
  remaining_amount_eur: string | null;
  /** Language the customer booked in, and the currency they pay in. */
  language: "pl" | "en" | "de";
  payment_currency: Currency;
  payment_link_sent_at: string | null;
  confirmed_at: string | null;
  payment_deadline: string | null;
  paid_at: string | null;
  remainder_paid_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  tracking_code: string;
  tracking_code_valid_from: string | null;
  tracking_code_expires_at: string | null;
  assigned_driver_id: number | null;
  assigned_driver_name: string | null;
}
