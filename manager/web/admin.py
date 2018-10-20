from django.contrib import admin
from . import models


# Register your models here.
admin.site.register(models.ConfigFile)
admin.site.register(models.Agent)
admin.site.register(models.Task)
admin.site.register(models.Token)
