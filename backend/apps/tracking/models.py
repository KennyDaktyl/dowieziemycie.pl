from django.db import models


class PositionPing(models.Model):
    """One GPS fix from a driver's app while they're on an active booking
    (KIEROWCA_W_DRODZE/W_TRAKCIE) — Driver.current_lat/lng only ever holds
    the latest fix, so this is the only history available to reconstruct
    "how many km did the driver actually cover" once a ride finishes."""

    driver = models.ForeignKey("fleet.Driver", on_delete=models.CASCADE, related_name="position_pings")
    booking = models.ForeignKey(
        "bookings.Booking", on_delete=models.CASCADE, related_name="position_pings", null=True, blank=True,
    )
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["booking", "recorded_at"])]
