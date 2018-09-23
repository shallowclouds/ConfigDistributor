# import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
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
        return render(
            request,
            "config/list.html",
            {"sources": {"title": "配置文件列表", "configs": res}}
            )


class ConfigProfileView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        try:
            query = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件列表-404"},
                "errors": [const.CONFIG_NOT_FOUND, ]
                })
        res = serializers.ConfigSerializer(query)
        return render(
            request,
            "config/profile.html",
            {"sources": {"title": "配置文件列表", "configs": res.data}}
            )


class ConfigAddView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        return render(
            request,
            "config/add.html",
            {"sources": {"title": "添加配置文件"}}
            )

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request):
        config = models.ConfigFile(
            name=request.POST["name"],
            status=request.POST["status"],
            description=request.POST["description"],
            path=request.POST["path"],
            contents=request.POST["content"]
            )
        config.save()
        return redirect("ConfigProfile", config.id)


class ConfigEditView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        try:
            query = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件不存在-404"},
                "errors": [const.CONFIG_NOT_FOUND, ]
                })
        res = serializers.ConfigSerializer(query)
        return render(
            request,
            "config/edit.html",
            {"sources": {"title": "编辑配置文件", "configs": res.data}}
            )

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        try:
            config = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件不存在-404"},
                "errors": [const.CONFIG_NOT_FOUND, ]})
        config.name = request.POST["name"]
        config.description = request.POST["description"]
        config.path = request.POST["path"]
        config.contents = request.POST["content"]
        config.status = request.POST["status"]
        config.save()
        return redirect("ConfigProfile", id)


class ConfigDeleteView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        try:
            query = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件不存在-404"},
                "errors": [const.CONFIG_NOT_FOUND, ]})
        res = serializers.ConfigSerializer(query)
        return render(request, "config/delete.html", {
            "sources": {
                "title": "删除配置文件", "configs": res.data
                }
                })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        try:
            config = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件不存在-404"},
                "errors": [const.CONFIG_NOT_FOUND, ]})
        config.delete()
        return redirect("ConfigList")


class ConfigDiffView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id1=None, id2=None):
        pass


class AgentListView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        query = models.Agent.objects.all()
        res = serializers.AgentSerializer(query, many=True)
        res = res.data
        return render(request, "agent/list.html", {
            "sources": {"title": "服务器列表", "agents": res}})


class AgentProfileView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        try:
            query = models.Agent.objects.get(id=id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "服务器-404"},
                "errors": [const.AGENT_NOT_FOUND, ]})
        res = serializers.AgentSerializer(query)
        return render(request, "agent/profile.html", {"sources": {
            "title": "服务器列表",
            "agents": res.data}})


class AgentAddView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        query = models.ConfigFile.objects.all()
        res = serializers.ConfigSerializerForAgent(query, many=True)
        res = res.data
        return render(request, "agent/add.html", {
            "sources": {"title": "添加服务器", "configs": res}
            })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request):
        print(request.POST.getlist("configs[]"))
        agent = models.Agent(
            name=request.POST["name"],
            status=request.POST["status"],
            ip_address=request.POST["ip_address"],
            )
        agent.save()
        configs = request.POST.getlist("configs[]")
        for id in configs:
            try:
                config = models.ConfigFile.objects.get(id=id)
            except models.ConfigFile.DoesNotExist:
                continue
            agent.configs.add(config)
        agent.save()
        return redirect("AgentProfile", agent.id)


class AgentDeleteView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        try:
            query = models.Agent.objects.get(id=id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件不存在-404"},
                "errors": [const.AGENT_NOT_FOUND, ]})
        res = serializers.AgentSerializer(query)
        return render(request, "agent/delete.html", {
            "sources": {
                "title": "删除服务器", "agents": res.data
                }
                })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        try:
            agent = models.Agent.objects.get(id=id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "配置文件不存在-404"},
                "errors": [const.AGENT_NOT_FOUND, ]})
        agent.delete()
        return redirect("AgentList")


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
            auth_res = auth.authenticate(
                request,
                username=request.POST["username"],
                password=request.POST["password"])
            if auth_res and auth_res.is_active:
                auth.login(request, auth_res)
                if "next" in request.GET:
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    return HttpResponseRedirect(reverse("ConfigList"))
            else:
                return render(request, "auth/login.html", {
                    "error": [const.LOGIN_ERROR_TIP]})
        else:
            return render(request, "auth/login.html", {
                "error": [const.LOGIN_ERROR_EMPTY_TIP]})


class AuthLogoutView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect(reverse("AuthLogin"))


class PushView(View):
    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        pass
