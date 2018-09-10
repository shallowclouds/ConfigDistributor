import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from manager import const

from . import models, serializers


class ConfigListView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        query = models.ConfigFile.objects.all()
        res = serializers.ConfigSerializer(query, many=True)
        res = res.data
        return render(request, "config/list.html", {"sources": {"title": "配置文件列表", "configs": res}})


class ConfigProfileView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        try:
            query = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "config/profile.html", {"sources": {"title": "配置文件列表-404"},  "errors": [const.CONFIG_NOT_FOUND, ]})
        res = serializers.ConfigSerializer(query)
        return render(request, "config/profile.html", {"sources": {"title": "配置文件列表", "configs": res.data}})


class ConfigAddView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        return render(request, "config/add.html", {"sources": {"title": "添加配置文件"}})

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request):
        pass


class ConfigEditView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id=None):
        pass


class ConfigDeleteView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id=None):
        pass


class ConfigDiffView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id1=None, id2=None):
        pass


class AgentListView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        pass


class AgentProfileView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass


class AgentAddView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        pass

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request):
        pass


class AgentEditView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id=None):
        pass


class AgentAddconfigView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id=None):
        pass


class AuthLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("ConfigList"))
        return render(request, "auth/login.html")

    def post(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("ConfigList"))

        if "username" in request.POST and "password" in request.POST:
            auth_res = auth.authenticate(request, username=request.POST["username"], password=request.POST["password"])
            if auth_res and auth_res.is_active:
                auth.login(request, auth_res)
                if "next" in request.GET:
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    return HttpResponseRedirect(reverse("ConfigList"))
            else:
                return render(request, "auth/login.html", {"error": [const.LOGIN_ERROR_TIP]})
        else:
            return render(request, "auth/login.html", {"error": [const.LOGIN_ERROR_EMPTY_TIP]})


class AuthLogoutView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect(reverse("AuthLogin"))


class PushView(View):
    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass
