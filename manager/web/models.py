from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class UserProfile(models.Model):

    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    id = models.AutoField("ID", primary_key=True)


class ConfigFile(models.Model):

    STATUS_CHOICES = (
        ("正常", "该配置文件正常"),
        ("未完成", "该配置文件未配置文成"),
        ("停用", "该配置文件已被停用"),
    )

    id = models.AutoField("ID", primary_key=True)
    name = models.CharField("name", max_length=30, default="Unnamed")
    status = models.CharField("status", max_length=20, choices=STATUS_CHOICES, default="正常")
    contents = models.TextField("contents", default="")
    create_time = models.DateTimeField("create time", default=timezone.now)


class Server(models.Model):

    STATUS_CHOICES = (
        ("正常", "该节点与服务器连接正常"),
        ("连接断开", "该节点与服务器连接已断开"),
        ("未连接", "该节点未与服务器建立连接"),
    )

    id = models.AutoField("ID", primary_key=True)
    ip_address = models.GenericIPAddressField("ip address", protocol="IPv4", default="127.0.0.1")
    status = models.CharField("status", max_length=20, choices=STATUS_CHOICES, default="未连接")


    

