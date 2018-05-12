from django.urls import path, include
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('list/', views.WebListView.as_view(), name="WebList"),
    path('login/', views.WebLoginView.as_view(), name="WebLogin"),
    path('logout/', views.WebLogoutView.as_view(), name="WebLogout"),
    path('agent/', TemplateView.as_view(template_name="func/agent.html")),
    path('diff/', TemplateView.as_view(template_name="func/diff.html")),
    path('config/', TemplateView.as_view(template_name="func/config.html")),
    path('text/', TemplateView.as_view(template_name="func/text.html")),
]
