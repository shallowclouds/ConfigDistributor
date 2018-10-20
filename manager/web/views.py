import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from manager import const

from . import models, serializers
from . import msgq

msgqs = msgq.MessageQ()


class ConfigListView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        query = models.ConfigFile.objects.all()
        res = serializers.ConfigSerializer(query, many=True)
        res = res.data
        return render(
            request,
            "config/list.html",
            {"sources": {"title": "Config List", "configs": res}}
            )


class ConfigProfileView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        try:
            query = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Config Detail"},
                "errors": [const.CONFIG_NOT_FOUND, ]
                })
        res = serializers.ConfigSerializer(query)
        return render(
            request,
            "config/profile.html",
            {"sources": {"title": "Config List", "configs": res.data}}
            )


class ConfigAddView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        return render(
            request,
            "config/add.html",
            {"sources": {"title": "Add Config"}}
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
                "sources": {"title": "Config Not Found"},
                "errors": [const.CONFIG_NOT_FOUND, ]
                })
        res = serializers.ConfigSerializer(query)
        return render(
            request,
            "config/edit.html",
            {"sources": {"title": "Edit Config", "configs": res.data}}
            )

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        try:
            config = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Config Not Found"},
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
                "sources": {"title": "Config Not Found"},
                "errors": [const.CONFIG_NOT_FOUND, ]})
        res = serializers.ConfigSerializer(query)
        return render(request, "config/delete.html", {
            "sources": {
                "title": "Delete Config", "configs": res.data
                }
                })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        try:
            config = models.ConfigFile.objects.get(id=id)
        except models.ConfigFile.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Config Not Found"},
                "errors": [const.CONFIG_NOT_FOUND, ]})
        config.delete()
        return redirect("ConfigList")


class ConfigDiffView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id1=None, id2=None):
        if id1 and id2:
            ctx = const.CONTEXT_ORIGIN
            try:
                config1 = models.ConfigFile.objects.all().get(id=id1)
                config2 = models.ConfigFile.objects.all().get(id=id2)
            except models.ConfigFile.DoesNotExist:
                ctx["sources"]["title"] = "Config Not Found"
                ctx["errors"].append(const.CONFIG_NOT_FOUND)
                return render(request, "base.html", ctx)
            ctx["sources"]["title"] = "Config File Diff"
            ctx["sources"]["config_first"] = serializers.ConfigSerializer(config1).data
            ctx["sources"]["config_second"] = serializers.ConfigSerializer(config2).data
            return render(request, "config/diff.html", ctx)
        else:
            ctx = const.CONTEXT_ORIGIN
            configs = models.ConfigFile.objects.all()
            ctx["sources"]["title"] = "Choose to Diff"
            ctx["sources"]["configs"] = serializers.ConfigSerializerForAgent(
                configs,
                many=True
                ).data
            return render(request, "config/diff_choose.html", ctx)


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
                "sources": {"title": "Server Not Found"},
                "errors": [const.AGENT_NOT_FOUND, ]})
        res = serializers.AgentSerializer(query)
        return render(request, "agent/profile.html", {"sources": {
            "title": "Server List",
            "agents": res.data}})


class AgentAddView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        query = models.ConfigFile.objects.all()
        res = serializers.ConfigSerializerForAgent(query, many=True)
        res = res.data
        return render(request, "agent/add.html", {
            "sources": {"title": "Add Server", "configs": res}
            })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request):
        # print(request.POST.getlist("configs[]"))
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
                "sources": {"title": "Config Not Found"},
                "errors": [const.AGENT_NOT_FOUND, ]})
        res = serializers.AgentSerializer(query)
        return render(request, "agent/delete.html", {
            "sources": {
                "title": "Delete Server", "agents": res.data
                }
                })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        try:
            agent = models.Agent.objects.get(id=id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Server Not Found"},
                "errors": [const.AGENT_NOT_FOUND, ]
            })
        agent.delete()
        return redirect("AgentList")


class AgentEditView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id):
        config = models.ConfigFile.objects.all()
        configs = serializers.ConfigSerializerForAgent(config, many=True)
        try:
            agent = models.Agent.objects.get(id=id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Server Not Found"},
                "errors": [const.AGENT_NOT_FOUND, ]
            })
        res = serializers.AgentSerializer(agent)
        return render(request, "agent/edit.html", {
            "sources": {
                "title": "Edit Server Profile",
                "agents": res.data,
                "configs": configs.data
                },
        })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id):
        new_configs = request.POST.getlist("configs[]")
        try:
            agent = models.Agent.objects.get(id=id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Server Not Found"},
                "errors": [const.AGENT_NOT_FOUND, ]
            })
        agent.name = request.POST["name"]
        agent.ip_address = request.POST["ip_address"]
        agent.status = request.POST["status"]
        agent.save()
        new_config_list = list()
        for id in new_configs:
            try:
                config = models.ConfigFile.objects.get(id=id)
            except models.ConfigFile.DoesNotExist:
                continue
            new_config_list.append(config)
        agent.configs.set(new_config_list)
        return redirect("AgentProfile", agent.id)


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


class AuthUserView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        ctx = const.CONTEXT_ORIGIN

        if id is None:
            users = User.objects.all()
            users_list = serializers.UserSerializer(users, many=True)
            ctx["sources"] = {
                "title": "User List",
                "users": users_list.data,
            }
            return render(request, "auth/user_list.html", ctx)

        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            ctx["sources"]["title"] = "用户不存在-404"
            ctx["errors"] = [const.USER_NOT_FOUND, ]
            return render(request, "base.html", ctx)
        users = serializers.UserSerializer(user)
        ctx["sources"] = {
            "title": "User Profile",
            "users": users.data,
        }
        return render(request, "auth/user_profile.html", ctx)

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id=None):
        if id is None:
            # add user
            new_user = User.objects.create_superuser(
                request.POST["username"],
                request.POST["email"],
                request.POST["password"]
                )
            return redirect("AuthUserById", new_user.id)

        ctx = const.CONTEXT_ORIGIN
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            ctx["sources"]["title"] = "User Not Found"
            ctx["errors"] = [const.USER_NOT_FOUND, ]
            return render(request, "base.html", ctx)
        user.username = request.POST["username"]
        user.email = request.POST["email"]
        if request.POST["password"] != "":
            user.set_password(request.POST["password"])
        user.save()
        return redirect("AuthUserById", user.id)


@login_required(login_url="AuthLogin")
def AuthUserDeleteView(request, id):
    ctx = const.CONTEXT_ORIGIN
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        ctx["sources"]["title"] = "User Not Found"
        ctx["errors"] = [const.USER_NOT_FOUND, ]
        return render(request, "base.html", ctx)
    user.delete()
    return redirect("AuthUser")


class PushView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        ctx = const.CONTEXT_ORIGIN
        if id:
            try:
                agent = models.Agent.objects.all().get(id=id)
            except models.Agent.DoesNotExist:
                ctx["errors"].append(const.AGENT_NOT_FOUND)
                return render(request, "base.html", ctx)
            configs = agent.configs.all()
            ctx["sources"]["title"] = "Push Configs"
            ctx["sources"]["configs"] = serializers.ConfigSerializer(
                configs,
                many=True
                ).data
            ctx["sources"]["agents"] = [serializers.AgentSerializer(agent).data, ]
            return render(request, "task/push_task.html", ctx)
        else:
            agents = models.Agent.objects.all()
            configs = models.ConfigFile.objects.all()
            ctx["sources"]["title"] = "Push Configs"
            ctx["sources"]["configs"] = serializers.ConfigSerializer(
                configs,
                many=True
                ).data
            ctx["sources"]["agents"] = serializers.AgentSerializer(
                agents,
                many=True
                ).data
            return render(request, "task/push_task.html", ctx)

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, id=None):
        config_id_list = request.POST.getlist("configs[]")
        agent_id_list = request.POST.getlist("agents[]")
        configs = [models.ConfigFile.objects.all().get(id=id) for id in config_id_list]
        agents = [models.Agent.objects.all().get(id=id) for id in agent_id_list]
        task_data = {
            "type": "POST",
            "client_list": [{"id": agent.id, "ip_address": agent.ip_address} for agent in agents],
            "file_list": [{"remote_path": config.path, "file_content_b64": config.contents} for config in configs],
        }
        # print(task_data)
        taskid = msgqs.push_task(task_data)
        return redirect("TaskProfile", id=taskid)


class PullView(View):
    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        ctx = const.CONTEXT_ORIGIN
        try:
            agent = models.Agent.objects.all().get(id=id)
        except models.Agent.DoesNotExist:
            ctx["sources"]["title"] = "Server Not Found"
            ctx["errors"] = [const.AGENT_NOT_FOUND]
            return (request, "base.html", ctx)
        task = dict()
        task["type"] = "GET"
        task["client_list"] = [{
            "id": agent.id,
            "ip_address": agent.ip_address
            }]
        task["remote_path"] = []
        for config in agent.configs.all():
            task["remote_path"].append(config.path)
        tid = msgqs.push_task(task)
        return redirect("TaskProfile", id=tid)


class TaskView(View):
    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id=None):
        if id:
            msgqs.get_results()
            ctx = const.CONTEXT_ORIGIN
            try:
                ttask = models.Task.objects.all().get(id=id)
            except models.Task.DoesNotExist:
                ctx["sources"]["title"] = "Task Not Found"
                ctx["errors"] = [const.TASK_NOT_FOUND]
                return render(request, "base.html", ctx)
            task_data = serializers.TaskSerializer(ttask)
            ctx["sources"]["tasks"] = task_data.data
            if ttask.has_result:
                # print(json.loads(ttask.result))
                ctx["sources"]["tasks"]["result"] = json.loads(ttask.result)
            # print(ctx["sources"]["tasks"]["result"])
            ctx["sources"]["tasks"]["task"] = json.loads(ttask.task)
            ctx["sources"]["title"] = "Task Detail"
            # print(ctx)
            return render(request, "task/profile.html", ctx)
        else:
            msgqs.get_results()
            tasks = models.Task.objects.all()[:20]
            tasks_data = serializers.TaskSerializer(tasks, many=True)
            ctx = const.CONTEXT_ORIGIN
            ctx["sources"]["title"] = "Task List"
            ctx["sources"]["tasks"] = tasks_data.data
            ctx["errors"] = []
            return render(request, "task/list.html", ctx)


class TestConnectionView(View):

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id=None):
        task_data = const.TEST_TASK.copy()
        task_data["client_list"] = list()
        if agent_id:
            ctx = const.CONTEXT_ORIGIN
            try:
                agent = models.Agent.objects.all().get(id=agent_id)
            except models.Task.DoesNotExist:
                ctx["sources"]["title"] = "Server Not Found"
                ctx["errors"].append(const.AGENT_NOT_FOUND)
                return render(request, "base.html", ctx)
            task_data["client_list"] = [({"id": agent.id, "ip_address": agent.ip_address}), ]
            task_id = msgqs.push_task(task_data)
            return redirect("TaskProfile", task_id)
        else:
            agents = models.Agent.objects.all()
            for agent in agents:
                task_data["client_list"].append({"id": agent.id, "ip_address": agent.ip_address})
            task_id = msgqs.push_task(task_data)
            return redirect("TaskProfile", task_id)
