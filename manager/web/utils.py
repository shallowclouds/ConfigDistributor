from django.shortcuts import redirect
from django.contrib import messages
import hashlib
import uuid
from django.utils import timezone


def redirect_error_view(request, redirect_to=None, errors=None):
    """
    add errors to message and redirect to a new page
    :param request: request
    :param redirect_to: the View you want to redirect to
    :param errors: a string you want to add to messages
    :return: response for the redirecting
    """
    if errors:
        messages.error(request, errors)
    return redirect(redirect_to)


def generate_token():
    """
    generate a new token, new token is md5(uuid+timestamp)
    :return: the generated token
    """
    t_uuid = str(uuid.uuid1())
    t_token = hashlib.md5((t_uuid+str(timezone.now())).encode(encoding="utf-8")).digest().hex()
    return t_token

