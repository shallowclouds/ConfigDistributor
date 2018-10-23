from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from . import token

# url patterns for config views
config_urls = [
    # the configs list
    path('', views.ConfigListView.as_view(), name="ConfigList"),
    # the profile of the config identified by the config id
    path(
        'profile/<int:config_id>/',
        views.ConfigProfileView.as_view(),
        name="ConfigProfile"
        ),
    # edit the profile of the config identified by the config id
    path('edit/<int:config_id>/', views.ConfigEditView.as_view(), name="ConfigEdit"),
    # delete the config identified by the config id
    path(
        'delete/<int:config_id>/',
        views.ConfigDeleteView.as_view(),
        name="ConfigDelete"
        ),
    # add new config file from a form or a json file
    path('add/', views.ConfigAddView.as_view(), name="ConfigAdd"),
    # diff two config files identified by the configs' id
    path(
        'diff/<int:id1>/<int:id2>/',
        views.ConfigDiffView.as_view(),
        name="ConfigDiffById"
        ),
    # choose the config file to diff
    path('diff/', views.ConfigDiffView.as_view(), name="ConfigDiffChoose"),
]

# url patterns for agent views
agent_urls = [
    # show the agent list
    path('', views.AgentListView.as_view(), name="AgentList"),
    # show the profile of the agent identified by the agent id
    path(
        'profile/<int:agent_id>/',
        views.AgentProfileView.as_view(),
        name="AgentProfile"
        ),
    # add a new agent from a form
    path('add/', views.AgentAddView.as_view(), name="AgentAdd"),
    # edit the profile of the agent identified by the agent id
    path('edit/<int:agent_id>/', views.AgentEditView.as_view(), name="AgentEdit"),
    # delete the agent identified by the agent id
    path(
        'delete/<int:agent_id>/',
        views.AgentDeleteView.as_view(),
        name="AgentDelete"
        ),
    # choose agents and configs and push config files to the servers
    path('push/', views.PushView.as_view(), name="Push"),
    # choose config files from certain agent
    path('push/<int:agent_id>/', views.PushView.as_view(), name="PushById"),
    # test the connection of all servers
    path('test/', views.TestConnectionView.as_view(), name="TestConnection"),
    # test the agent's connection
    path('test/<int:agent_id>/', views.TestConnectionView.as_view(), name="TestConnectionById"),
]

# url patterns for auth views
auth_urls = [
    # login page and user login
    path('login/', views.AuthLoginView.as_view(), name="AuthLogin"),
    # logout the user
    path('logout/', views.AuthLogoutView.as_view(), name="AuthLogout"),
    # show the list of the users
    path('user/', views.AuthUserView.as_view(), name="AuthUser"),
    # show the profile of the user identified by the user id
    path('user/<int:user_id>/', views.AuthUserView.as_view(), name="AuthUserById"),
    # add new user
    path(
        'user/add/',
        TemplateView.as_view(template_name="auth/user_add.html"),
        name="AuthUserAdd"
        ),
    # delete the user identified by the user id
    path(
        'user/delete/<int:user_id>/',
        views.auth_user_delete_view,
        name="AuthUserDelete",
        ),
    # generate a api token for the user
    path('token/generate/', token.generate_token_view, name="GenerateToken"),
    # show the token list
    path('token/', token.TokenView.as_view(), name="TokenList"),
    # delete the token
    path('token/delete/<int:token_id>/', token.TokenView.as_view(), name="TokenDelete"),
]

# url patterns for tasks view
task_urls = [
    # pull the config files from the agent identified by the agent id
    path('pull/<int:agent_id>/', views.PullView.as_view(), name="PullById"),
    # show the task list
    path('list/', views.TaskView.as_view(), name="TaskList"),
    # show the profile of the task identified by the task id
    path('profile/<int:task_id>/', views.TaskView.as_view(), name="TaskProfile"),
    # repeat the task identified by the task id
    path('redo/<int:task_id>/', views.redo_task_view, name="TaskRedo"),
]

# main url patterns
urlpatterns = [
    path('config/', include(config_urls)),
    path('agent/', include(agent_urls)),
    path('auth/', include(auth_urls)),
    path('task/', include(task_urls)),
]
