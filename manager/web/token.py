from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from manager import const
from django.contrib import messages
# from django.contrib.auth.models import User

from . import models, serializers


@login_required(login_url="AuthLogin")
def generate_token_view(request):
    """
    generate a token for the user
    :param request: http request of django
    :return: response of redirecting token list
    """
    token_ = models.Token(user=request.user)
    token_.refresh_token()
    token_.save()
    return redirect("TokenList")


class TokenView(View):
    """
    get: if has token id then delete the token identified by the token id, else show the list of all tokens
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, token_id=None):
        ctx = const.CONTEXT_ORIGIN
        if token_id:
            try:
                token_ = models.Token.objects.get(id=token_id)
            except models.Token.DoesNotExist:
                messages.error(request, const.TOKEN_NOT_FOUND)
                return redirect("TokenList")
            token_.delete()
            messages.success(request, const.TOKEN_SUCCESSFULLY_DELETED)
            return redirect("TokenList")
        else:
            tokens = models.Token.objects.all()
            tokens_list = serializers.TokenSerializer(tokens, many=True).data

            ctx["sources"]["title"] = "Token List"
            ctx["sources"]["tokens"] = tokens_list
            return render(request, "auth/token_list.html", ctx)
