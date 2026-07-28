from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

from .models import Customer


class CustomerJWTAuthentication(JWTAuthentication):
    """Resolves the JWT subject to `apps.accounts.Customer`, not `auth.User`.

    Customers log in with phone + OTP only — they never get a Django auth
    User row, so the stock JWTAuthentication (which looks up AUTH_USER_MODEL)
    can't be used as-is.
    """

    def get_user(self, validated_token):
        try:
            customer_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token nie zawiera identyfikatora klienta.")
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise InvalidToken("Klient nie istnieje.")
        customer.is_authenticated = True
        return customer
