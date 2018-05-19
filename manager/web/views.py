from django.shortcuts import render
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from manager import const


class WebListView(View):

    @method_decorator(login_required(login_url="WebLogin"))
    def get(self, request):
        return render(request, "func/list.html", {"sources": {"title": "服务器列表"}})


class WebLoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("WebList"))
        return render(request, "user/login.html")

    def post(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("WebList"))

        if "username" in request.POST and "password" in request.POST:
            auth_res  = auth.authenticate(request, username=request.POST["username"], password=request.POST["password"])
            if auth_res and auth_res.is_active:
                auth.login(request, auth_res)
                if "next" in request.GET:
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    return HttpResponseRedirect(reverse("WebList"))
            else:
                return render(request, "user/login.html", {"error":[const.LOGIN_ERROR_TIP]})
        else:
            return render(request, "user/login.html", {"error": [const.LOGIN_ERROR_EMPTY_TIP]})


class WebLogoutView(View):

    @method_decorator(login_required(login_url="WebLogin"))
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect(reverse("WebLogin"))

