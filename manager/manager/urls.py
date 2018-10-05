from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name="index"),
    path('web/', include('web.urls')),
    path('api/', include('apis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, 
        document_root=settings.STATIC_ROOT
        )
    urlpatterns.append(path('admin/', admin.site.urls))
