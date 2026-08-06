from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0021_backfill_price_eur"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="child_seat_ages",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Wiek dzieci, dla których trzeba przygotować fotelik lub podkładkę.",
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="bike_count",
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text="Liczba rowerów do przewiezienia na bagażniku Thule VeloSpace (0-4).",
                validators=[MinValueValidator(0), MaxValueValidator(4)],
            ),
        ),
    ]
