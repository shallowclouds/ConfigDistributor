from django.urls import path, include
from . import views
# from django.views.generic import TemplateView

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
        name="ConfigDiff"
        ),
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
    path(
        'addConfig/<int:id>/',
        views.AgentAddconfigView.as_view(),
        name="AgentAddconfig"
        ),
]

auth_urls = [
    path('login/', views.AuthLoginView.as_view(), name="AuthLogin"),
    path('logout/', views.AuthLogoutView.as_view(), name="AuthLogout"),
]

push_urls = [
    path('', views.PushView.as_view(), name="Push"),
]

urlpatterns = [
    path('config/', include(config_urls)),
    path('agent/', include(agent_urls)),
    path('auth/', include(auth_urls)),
    path('push/', include(push_urls)),
]
