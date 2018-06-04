from django.urls import path, include
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('list/', views.WebAgentView.as_view(), name="WebList"),
    path('login/', views.WebLoginView.as_view(), name="WebLogin"),
    path('logout/', views.WebLogoutView.as_view(), name="WebLogout"),
    path('agent/<int:id>/', views.WebAgentView.as_view(), name="WebAgent"),
    path('diff/<int:id1>/<int:id2>/', views.WebConfigDiffView.as_view(), name="WebConfigDiff"),
    path('config/', views.WebConfigView.as_view(), name="WebConfigList"),
    path('config/<int:id>/', views.WebConfigView.as_view(), name="WebConfig"),
]
