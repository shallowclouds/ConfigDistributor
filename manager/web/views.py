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
    pass


class ConfigProfileView(View):
    pass


class ConfigAddView(View):
    pass


class ConfigEditView(View):
    pass


class ConfigDeleteView(View):
    pass


class ConfigDiffView(View):
    pass


class AgentListView(View):
    pass


class AgentProfileView(View):
    pass


class AgentAddView(View):
    pass


class AgentEditView(View):
    pass


class AgentAddconfigView(View):
    pass


class AgentAddconfigByIdView(View):
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
    pass


class WebConfigView(View):

    @method_decorator(login_required(login_url="WebLogin"))
    def get(self, request, id=None):
        if id:
            try:
                query = models.ConfigFile.objects.get(id=id)
            except models.ConfigFile.DoesNotExist:
                return render(request, "func/text.html", {"sources": {"title": "配置文件列表-404"},  "errors": [const.CONFIG_NOT_FOUND, ]})
            res = serializers.ConfigSerializer(query)
            return render(request, "func/text.html", {"sources": {"title": "配置文件列表", "configs": res.data}})
        else:
            query = models.ConfigFile.objects.all()
            res = serializers.ConfigSerializer(query, many=True)
            return render(request, "func/config.html", {"sources": {"title": "配置文件列表", "configs": res.data}})


class WebConfigDiffView(View):

    @method_decorator(login_required(login_url="WebLogin"))
    def get(self, request, id1=1, id2=1):
        return render(request, "func/diff.html", {})


class WebAgentView(View):

    @method_decorator(login_required(login_url="WebLogin"))
    def get(self, request, id=None):
        if id:
            try:
                query = models.Agent.objects.get(id=id)
            except models.Agent.DoesNotExist:
                return render(request, "func/agent.html", {"sources": {"title": "服务器列表-404"},  "errors": [const.CONFIG_NOT_FOUND, ]})
            res = serializers.AgentSerializer(query)
            return render(request, "func/agent.html", {"sources": {"title": "服务器列表", "agents": res.data}})
        else:
            query = models.Agent.objects.all()
            res = serializers.AgentSerializer(query, many=True)
            return render(request, "func/list.html", {"sources": {"title": "服务器列表", "agents": res.data}})


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
