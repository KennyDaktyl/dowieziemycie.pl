from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

from .models import Driver


class DriverJWTAuthentication(JWTAuthentication):
    """Resolves the JWT subject to `apps.fleet.Driver`, not `auth.User`.

    Mirrors apps.accounts.authentication.CustomerJWTAuthentication — the
    driver-login token's subject is the Driver row itself (see
    DriverLoginView / VerifyOtpView), not the underlying Django User.
    """

    def get_user(self, validated_token):
        try:
            driver_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token nie zawiera identyfikatora kierowcy.")
        try:
            driver = Driver.objects.select_related("vehicle").get(pk=driver_id)
        except Driver.DoesNotExist:
            raise InvalidToken("Kierowca nie istnieje.")
        driver.is_authenticated = True
        return driver
