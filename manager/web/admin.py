from django.contrib import admin
from . import models
from django.contrib.auth.models import User


# try:
#     first_user = User.objects.all()[0]
# except Exception:
#     new_user = User.objects.create_superuser(
#                 "admin",
#                 "i@yorling.com",
#                 "qaq@qwq1379?!moe"
#                 )
#     print("create initial user")
# Register your models here.
admin.site.register(models.ConfigFile)
admin.site.register(models.Agent)
