from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from manager import const
# from django.contrib.auth.models import User

from . import models, serializers


@login_required(login_url="AuthLogin")
def generate_token_view(request):
    token_ = models.Token(user=request.user)
    token_.refresh_token()
    token_.save()
    return redirect("TokenList")


class TokenView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        ctx = const.CONTEXT_ORIGIN
        if id:
            try:
                token_ = models.Token.objects.get(id=id)
            except models.Token.DoesNotExist:
                ctx["errors"].append("Token Not Found, or already deleted.")
                ctx["sources"]["title"] = "TokenNotFound"
                ctx["sources"]["users"]["id"] = request.user.id
                return render(request, "base.html", ctx)
            token_.delete()
            return redirect("TokenList")
        else:
            tokens = models.Token.objects.all()
            tokens_list = serializers.TokenSerializer(tokens, many=True).data

            ctx["sources"]["title"] = "Token List"
            ctx["sources"]["tokens"] = tokens_list
            return render(request, "auth/token_list.html", ctx)
