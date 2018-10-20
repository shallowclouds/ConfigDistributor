from rest_framework.authentication import TokenAuthentication
from .models import Token


class SimpleTokenAuthentication(TokenAuthentication):

    model = Token
