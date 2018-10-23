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
import logging
from django.contrib import messages
from .utils import redirect_error_view

msgqs = msgq.MessageQ()
logger = logging.getLogger(__name__)


class ConfigListView(View):
    """View for config list
    to show the list of config files in the databases.

    """

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
    """View for config profile
    show the config identified by the config_id
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, config_id):
        try:
            query = models.ConfigFile.objects.get(id=config_id)
        except models.ConfigFile.DoesNotExist:
            messages.error(request, const.CONFIG_NOT_FOUND)
            return redirect("ConfigList")
        res = serializers.ConfigSerializer(query)
        return render(
            request,
            "config/profile.html",
            {"sources": {"title": "Config List", "configs": res.data}}
            )


class ConfigAddView(View):
    """View for adding config
    get: return the page for adding config
    post: add configs from a form or a json file
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        return render(
            request,
            "config/add.html",
            {"sources": {"title": "Add Config"}}
            )

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request):
        if request.POST["json"] == "false":
            # add single config file to database from form
            config = models.ConfigFile(
                name=request.POST["name"],
                status=request.POST["status"],
                description=request.POST["description"],
                path=request.POST["path"],
                contents=request.POST["content"]
                )
            config.save()
            messages.success(request, "Successfully add one config.")
            return redirect("ConfigProfile", config.id)
        else:
            # add multi config files from json file
            try:
                configs_content = request.FILES["JSONFile"].read().decode("utf-8")
                configs_data = json.loads(configs_content)
                success_configs = list()
                for config_ in configs_data["data"]:
                    new_config = models.ConfigFile(
                        name=config_["name"],
                        status=config_["status"],
                        description=config_["description"],
                        path=config_["path"],
                        contents=config_["content"]
                        )
                    success_configs.append(new_config)
                    # not save, if one fails then all configs in the json file won't be added to the database
            except Exception as e:
                # error occurred usually cause there are errors in the json file, no config will be added to database
                logger.error("Error occurred while import configs from json file:"+str(e))
                ctx = dict(const.CONTEXT_ORIGIN)
                ctx["sources"]["title"] = "File Format Not correct"
                messages.warning(request, 'Errors occurred while parsing json file, Please check the json file.')
                # return to the config adding page
                return redirect("ConfigAdd")
            for config_ in success_configs:
                config_.save()
            # save configs
            messages.success(request,
                             "Successfully add {config_count} configs".format(config_count=len(success_configs)))
            return redirect("ConfigList")


class ConfigEditView(View):
    """View for editing config
    get: return the page for editing config
    post: save changes to database
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, config_id):
        try:
            query = models.ConfigFile.objects.get(id=config_id)
        except models.ConfigFile.DoesNotExist:
            messages.error(request, const.CONFIG_NOT_FOUND)
            return redirect("ConfigList")
        res = serializers.ConfigSerializer(query)
        return render(
            request,
            "config/edit.html",
            {"sources": {"title": "Edit Config", "configs": res.data}}
            )

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, config_id):
        try:
            config = models.ConfigFile.objects.get(id=config_id)
        except models.ConfigFile.DoesNotExist:
            messages.error(request, const.CONFIG_NOT_FOUND)
            return redirect("ConfigList")
        config.name = request.POST["name"]
        config.description = request.POST["description"]
        config.path = request.POST["path"]
        config.contents = request.POST["content"]
        config.status = request.POST["status"]
        config.save()
        messages.success(request, "Successfully updated config's profile.")
        return redirect("ConfigProfile", config_id)


class ConfigDeleteView(View):
    """View for deleting a config file
    get: return a page ask user if be sure to delete this config file with the profile of the config file
    post: delete the config file identified by the config id
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, config_id):
        try:
            query = models.ConfigFile.objects.get(id=config_id)
        except models.ConfigFile.DoesNotExist:
            messages.error(request, const.CONFIG_NOT_FOUND)
            return redirect("ConfigList")
        res = serializers.ConfigSerializer(query)
        return render(request, "config/delete.html", {
            "sources": {
                "title": "Delete Config", "configs": res.data
                }
                })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, config_id):
        try:
            config = models.ConfigFile.objects.get(id=config_id)
        except models.ConfigFile.DoesNotExist:
            messages.error(request, const.CONFIG_NOT_FOUND)
            return redirect("ConfigList")
        config.delete()
        messages.success(request, const.CONFIG_SUCCESSFULLY_DELETED)
        return redirect("ConfigList")


class ConfigDiffView(View):
    """View for diffing two config file
    get: if id1 and id2 are not None the return the results of diffing, or ask user to choose two config file.
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, id1=None, id2=None):
        if id1 and id2:
            ctx = const.CONTEXT_ORIGIN
            try:
                config1 = models.ConfigFile.objects.all().get(id=id1)
                config2 = models.ConfigFile.objects.all().get(id=id2)
            except models.ConfigFile.DoesNotExist:
                return redirect_error_view(request, "ConfigDiffChoose", const.CONFIG_NOT_FOUND)
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
    """View for showing the list of agents

    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        query = models.Agent.objects.all()
        res = serializers.AgentSerializer(query, many=True)
        res = res.data
        return render(request, "agent/list.html", {
            "sources": {"title": "Server List", "agents": res}})


class AgentProfileView(View):
    """View for showing the profile of the agent identified by agent id

    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id):
        try:
            query = models.Agent.objects.get(id=agent_id)
        except models.Agent.DoesNotExist:
            return render(request, "base.html", {
                "sources": {"title": "Server Not Found"},
                "errors": [const.AGENT_NOT_FOUND, ]})
        res = serializers.AgentSerializer(query)
        return render(request, "agent/profile.html", {"sources": {
            "title": "Server List",
            "agents": res.data}})


class AgentAddView(View):
    """View for adding a agent from form
    get: return the page to let user add profile for agent
    post: add agent to database
    """

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
        agent = models.Agent(
            name=request.POST["name"],
            status=request.POST["status"],
            ip_address=request.POST["ip_address"],
            )
        agent.save()
        configs = request.POST.getlist("configs[]")
        for config_id in configs:
            try:
                config = models.ConfigFile.objects.get(id=config_id)
            except models.ConfigFile.DoesNotExist:
                # if the config not found, then omit it
                continue
            agent.configs.add(config)
        agent.save()
        messages.success(request, const.AGENT_SUCCESSFULLY_ADDED)
        return redirect("AgentProfile", agent.id)


class AgentDeleteView(View):
    """View for deleting a agent
    get: return the page to make sure user want to delete this agent
    post: delete agent from database
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id):
        try:
            query = models.Agent.objects.get(id=agent_id)
        except models.Agent.DoesNotExist:
            messages.error(request, const.AGENT_NOT_FOUND)
            return redirect("AgentList")
        res = serializers.AgentSerializer(query)
        return render(request, "agent/delete.html", {
            "sources": {
                "title": "Delete Server", "agents": res.data
                }
                })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, agent_id):
        try:
            agent = models.Agent.objects.get(id=agent_id)
        except models.Agent.DoesNotExist:
            messages.error(request, const.AGENT_NOT_FOUND)
            return redirect("AgentList")
        agent.delete()
        messages.success(request, const.AGENT_SUCCESSFULLY_DELETED)
        return redirect("AgentList")


class AgentEditView(View):
    """View for editing the profile of agent
    get: return a page to let user change profile of the agent identified by agent id
    post: change the profile and save changes to database
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id):
        config = models.ConfigFile.objects.all()
        configs = serializers.ConfigSerializerForAgent(config, many=True)
        try:
            agent = models.Agent.objects.get(id=agent_id)
        except models.Agent.DoesNotExist:
            messages.error(request, const.AGENT_NOT_FOUND)
            return redirect("AgentList")
        res = serializers.AgentSerializer(agent)
        return render(request, "agent/edit.html", {
            "sources": {
                "title": "Edit Server Profile",
                "agents": res.data,
                "configs": configs.data
                },
        })

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, agent_id):
        new_configs = request.POST.getlist("configs[]")
        try:
            agent = models.Agent.objects.get(id=agent_id)
        except models.Agent.DoesNotExist:
            messages.error(request, const.AGENT_NOT_FOUND)
            return redirect("AgentList")
        agent.name = request.POST["name"]
        agent.ip_address = request.POST["ip_address"]
        agent.status = request.POST["status"]
        agent.save()
        new_config_list = list()
        for agent_id in new_configs:
            try:
                config = models.ConfigFile.objects.get(id=agent_id)
            except models.ConfigFile.DoesNotExist:
                # if config not found, omit it
                continue
            new_config_list.append(config)
        # the agent's configs change to new set of configs
        agent.configs.set(new_config_list)
        messages.success(request, const.AGENT_SUCCESSFULLY_UPDATED)
        return redirect("AgentProfile", agent.id)


class AuthLoginView(View):
    """View for login
    get: return the login page for user to login
    post: check the username and password and login the user
    """

    def get(self, request):
        if request.user.is_authenticated:
            # if the user has login
            return HttpResponseRedirect(reverse("ConfigList"))
        return render(request, "auth/login.html")

    def post(self, request):
        if request.user.is_authenticated:
            # if the user has login
            return HttpResponseRedirect(reverse("ConfigList"))

        if "username" in request.POST and "password" in request.POST:
            auth_res = auth.authenticate(
                request,
                username=request.POST["username"],
                password=request.POST["password"])
            if auth_res and auth_res.is_active:
                # username and password and user is valid
                auth.login(request, auth_res)
                messages.info(request, const.USER_WELCOME_TIP)
                if "next" in request.GET:
                    # if has next to redirect to
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    return HttpResponseRedirect(reverse("ConfigList"))
            else:
                # not valid
                messages.error(request, const.LOGIN_ERROR_TIP)
                return redirect("AuthLogin")
        else:
            # doesn't has username or password field
            messages.error(request, const.LOGIN_ERROR_EMPTY_TIP)
            return redirect("AuthLogin")


class AuthLogoutView(View):
    """View for user to logout

    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect(reverse("AuthLogin"))


class AuthUserView(View):
    """View for users
    get: if has user id then show the profile of the user, else show the list of users
    post: if has user id then change the profile of the user, else add a new user
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, user_id=None):
        ctx = const.CONTEXT_ORIGIN

        if user_id is None:
            # show the user list
            users = User.objects.all()
            users_list = serializers.UserSerializer(users, many=True)
            ctx["sources"] = {
                "title": "User List",
                "users": users_list.data,
            }
            return render(request, "auth/user_list.html", ctx)

        # show the profile of the user identified by user id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect_error_view(request, "AuthUser", const.USER_NOT_FOUND)
        users = serializers.UserSerializer(user)
        ctx["sources"] = {
            "title": "User Profile",
            "users": users.data,
        }
        return render(request, "auth/user_profile.html", ctx)

    @method_decorator(login_required(login_url="AuthLogin"))
    def post(self, request, user_id=None):
        if user_id is None:
            # add user
            new_user = User.objects.create_superuser(
                request.POST["username"],
                request.POST["email"],
                request.POST["password"]
                )
            return redirect("AuthUserById", new_user.id)

        # change the profile of the user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect_error_view(request, "AuthUser", const.USER_NOT_FOUND)
        user.username = request.POST["username"]
        user.email = request.POST["email"]
        if len(request.POST["password"]) >= 8:
            user.set_password(request.POST["password"])
        else:
            return redirect_error_view(request, "AuthUser", const.USER_PASSWORD_INVALID)
        user.save()
        messages.success(request, const.USER_SUCCESSFULLY_UPDATED)
        return redirect("AuthUserById", user.id)


@login_required(login_url="AuthLogin")
def auth_user_delete_view(request, user_id):
    """
    View for deleting the user identified by user id
    :param request: the request
    :param user_id: the user's id
    :return: response of redirecting to user list
    """
    ctx = const.CONTEXT_ORIGIN
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        ctx["sources"]["title"] = "User Not Found"
        ctx["errors"] = [const.USER_NOT_FOUND, ]
        return render(request, "base.html", ctx)
    user.delete()
    return redirect("AuthUser")


class PushView(View):
    """View for pushing config files to servers
    get: if has agent_id then just show the agent and the agent's configs else show all agents and configs
    post: add POST tasks of the configs and agents to push configs to these servers into the task queue
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id=None):
        ctx = const.CONTEXT_ORIGIN
        if agent_id:
            try:
                agent = models.Agent.objects.all().get(id=agent_id)
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
    def post(self, request):
        config_id_list = request.POST.getlist("configs[]")
        agent_id_list = request.POST.getlist("agents[]")
        configs = [models.ConfigFile.objects.all().get(id=t_id) for t_id in config_id_list]
        agents = [models.Agent.objects.all().get(id=t_id) for t_id in agent_id_list]
        task_data = {
            "type": "POST",
            "client_list": [{"id": agent.id, "ip_address": agent.ip_address} for agent in agents],
            "file_list": [{"remote_path": config.path, "file_content_b64": config.contents} for config in configs],
        }
        task_id = msgqs.push_task(task_data)
        return redirect("TaskProfile", task_id)


class PullView(View):
    """View for pulling all the configs from the server
    get: add GET task to task queue
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id=None):
        ctx = const.CONTEXT_ORIGIN
        try:
            agent = models.Agent.objects.all().get(id=agent_id)
        except models.Agent.DoesNotExist:
            ctx["sources"]["title"] = "Server Not Found"
            ctx["errors"] = [const.AGENT_NOT_FOUND]
            return render(request, "base.html", ctx)
        task = dict()
        task["type"] = "GET"
        task["client_list"] = [{
            "id": agent.id,
            "ip_address": agent.ip_address
            }]
        task["remote_path"] = []
        for config in agent.configs.all():
            task["remote_path"].append(config.path)
        task_id = msgqs.push_task(task)
        return redirect("TaskProfile", task_id)


class TaskView(View):
    """View for view the tasks
    get: if has task_id then show the detail of the task, else show the tasks list
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, task_id=None):
        if task_id:
            msgqs.get_results()
            ctx = dict(const.CONTEXT_ORIGIN)
            try:
                cur_task = models.Task.objects.all().get(id=task_id)
            except models.Task.DoesNotExist:
                return redirect_error_view(request, "TaskList", const.TASK_NOT_FOUND)
            task_data = serializers.TaskSerializer(cur_task)
            ctx["sources"]["tasks"] = task_data.data
            if cur_task.has_result:
                # if the task has been completed
                ctx["sources"]["tasks"]["result"] = json.loads(cur_task.result)
            ctx["sources"]["tasks"]["task"] = json.loads(cur_task.task)
            ctx["sources"]["title"] = "Task Detail"
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
    """View for testing connection of the servers
    get: if has agent id then test the connection of the server, else test all servers' connection,
         add TEST task to task queue.
    """

    @method_decorator(login_required(login_url="AuthLogin"))
    def get(self, request, agent_id=None):
        task_data = dict(const.TEST_TASK)
        task_data["client_list"] = list()
        if agent_id:
            ctx = const.CONTEXT_ORIGIN
            try:
                agent = models.Agent.objects.all().get(id=agent_id)
            except models.Task.DoesNotExist:
                return redirect_error_view(request, "AgentList", const.AGENT_NOT_FOUND)
            task_data["client_list"] = [({"id": agent.id, "ip_address": agent.ip_address}), ]
            task_id = msgqs.push_task(task_data)
            return redirect("TaskProfile", task_id)
        else:
            agents = models.Agent.objects.all()
            for agent in agents:
                task_data["client_list"].append({"id": agent.id, "ip_address": agent.ip_address})
            task_id = msgqs.push_task(task_data)
            return redirect("TaskProfile", task_id)


@login_required(login_url="AuthLogin")
def redo_task_view(request, task_id):
    """
    repeat the task identified by the task id
    :param request: the http request
    :param task_id: the task's id which will be repeated
    :return: response for redirecting to the new task profile
    """
    try:
        cur_task = models.Task.objects.all().get(id=task_id)
    except models.Task.DoesNotExist:
        ctx = dict(const.CONTEXT_ORIGIN)
        ctx["errors"].append(const.TASK_NOT_FOUND)
        ctx["title"] = "Error"
        return render(request, "base.html", ctx)
    new_task_id = msgqs.push_task(json.loads(cur_task.task))
    return redirect('TaskProfile', new_task_id)
