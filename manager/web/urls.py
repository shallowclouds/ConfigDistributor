from django.urls import path, include
from . import views
from django.views.generic import TemplateView

config_urls = [
    path('', views.ConfigListView, name="ConfigList"),
    path('profile/<int:id>/', views.ConfigProfileView, name="ConfigProfile"),
    path('edit/<int:id>/', views.ConfigEditView, name="ConfigEdit"),
    path('delete/<int:id>/', views.ConfigDeleteView, name="ConfigDelete"),
    path('add/<int:id>/', views.ConfigAddView, name="ConfigAdd"),
    path('diff/<int:id1>/<int:id2>/', views.ConfigDiffView, name="ConfigDiff"),
]

agent_urls = [
    path('', views.AgentListView, name="AgentList"),
    path('profile/<int:id>/', views.AgentProfileView, name="AgentProfile"),
    path('add/<int:id>/', views.AgentAddView, name="AgentAdd"),
    path('edit/<int:id>/', views.AgentEditView, name="AgentEdit"),
    path('addConfig/<int:id>/', views.AgentAddconfigView, name="AgentAddconfig"),
]

auth_urls = [
    path('login/', views.AuthLogin, name="AuthLogin"),
    path('logout/', views.AuthLogout, name="AuthLogout"),
]

push_urls = [
    path('', views.PushView, name="Push"),
]

urlpatterns = [
    path('config/', include(config_urls)),
    path('agent/', include(agent_urls)),
    path('auth/', include(auth_urls)),
    path('push/', include(push_urls)),
]
