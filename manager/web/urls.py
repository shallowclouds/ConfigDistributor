from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from . import token

config_urls = [
    path('', views.ConfigListView.as_view(), name="ConfigList"),
    path(
        'profile/<int:id>/',
        views.ConfigProfileView.as_view(),
        name="ConfigProfile"
        ),
    path('edit/<int:id>/', views.ConfigEditView.as_view(), name="ConfigEdit"),
    path(
        'delete/<int:id>/',
        views.ConfigDeleteView.as_view(),
        name="ConfigDelete"
        ),
    path('add/', views.ConfigAddView.as_view(), name="ConfigAdd"),
    path(
        'diff/<int:id1>/<int:id2>/',
        views.ConfigDiffView.as_view(),
        name="ConfigDiffById"
        ),
    path('diff/', views.ConfigDiffView.as_view(), name="ConfigDiffChoose"),
]

agent_urls = [
    path('', views.AgentListView.as_view(), name="AgentList"),
    path(
        'profile/<int:id>/',
        views.AgentProfileView.as_view(),
        name="AgentProfile"
        ),
    path('add/', views.AgentAddView.as_view(), name="AgentAdd"),
    path('edit/<int:id>/', views.AgentEditView.as_view(), name="AgentEdit"),
    path(
        'delete/<int:id>/',
        views.AgentDeleteView.as_view(),
        name="AgentDelete"
        ),
    path('push/', views.PushView.as_view(), name="Push"),
    path('push/<int:id>/', views.PushView.as_view(), name="PushById"),
    path('test/', views.TestConnectionView.as_view(), name="TestConnection"),
    path('test/<int:agent_id>/', views.TestConnectionView.as_view(), name="TestConnectionById"),
]

auth_urls = [
    path('login/', views.AuthLoginView.as_view(), name="AuthLogin"),
    path('logout/', views.AuthLogoutView.as_view(), name="AuthLogout"),
    path('user/', views.AuthUserView.as_view(), name="AuthUser"),
    path('user/<int:id>/', views.AuthUserView.as_view(), name="AuthUserById"),
    path(
        'user/add/',
        TemplateView.as_view(template_name="auth/user_add.html"),
        name="AuthUserAdd"
        ),
    path(
        'user/delete/<int:id>/',
        views.AuthUserDeleteView,
        name="AuthUserDelete",
        ),
    path('token/generate/', token.generate_token_view, name="GenerateToken"),
    path('token/', token.TokenView.as_view(), name="TokenList"),
    path('token/delete/<int:id>/', token.TokenView.as_view(), name="TokenDelete"),
]

task_urls = [
    path('pull/<int:id>/', views.PullView.as_view(), name="PullById"),
    path('list/', views.TaskView.as_view(), name="TaskList"),
    path('profile/<int:id>/', views.TaskView.as_view(), name="TaskProfile"),
]

urlpatterns = [
    path('config/', include(config_urls)),
    path('agent/', include(agent_urls)),
    path('auth/', include(auth_urls)),
    path('task/', include(task_urls)),
]
