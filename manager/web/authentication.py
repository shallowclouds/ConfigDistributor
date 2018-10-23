from rest_framework.authentication import TokenAuthentication
from .models import Token


class SimpleTokenAuthentication(TokenAuthentication):
    """TokenAuthentication class
    subclass the TokenAuthentication for a new Token Model
    """

    model = Token
