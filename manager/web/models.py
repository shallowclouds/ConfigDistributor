from django.db import models
from django.utils import timezone
import uuid
import hashlib
# import base64
from django.contrib.auth.models import User


class ConfigFile(models.Model):

    STATUS_CHOICES = (
        ("正常", "正常"),
        ("未完成", "未完成"),
        ("停用", "停用"),
    )

    id = models.AutoField("ID", primary_key=True)
    name = models.CharField("name", max_length=30, default="Unnamed")
    status = models.CharField(
        "status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="正常"
        )
    contents = models.TextField("contents", default="")
    create_time = models.DateTimeField("create time", default=timezone.now)
    description = models.CharField("description", max_length=100, default="")
    # path = models.FilePathField("path", default="")
    path = models.CharField("file path", max_length=300, default="")
    is_deleted = models.BooleanField("is_deleted", default=False)

    def __str__(self):
        return self.name


class Agent(models.Model):

    STATUS_CHOICES = (
        ("正常", "正常"),
        ("连接断开", "连接断开"),
        ("未连接", "未连接"),
    )

    id = models.AutoField("ID", primary_key=True)
    ip_address = models.GenericIPAddressField(
        "ip address",
        protocol="IPv4",
        default="127.0.0.1"
        )
    status = models.CharField(
        "status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="未连接"
        )
    configs = models.ManyToManyField('ConfigFile', blank=True)
    create_time = models.DateTimeField("create time", default=timezone.now)
    name = models.CharField("name", max_length=30, default="unnamed")

    def __str__(self):
        return self.ip_address


class Task(models.Model):
    TYPE_CHOICES = (
        ("查看服务器配置文件", "GET"),
        ("推送服务器文件", "POST"),
        ("测试服务器连接", "TEST"),
    )
    id = models.AutoField("ID", primary_key=True)
    uuid = models.UUIDField("uuid", default=uuid.uuid1)
    task = models.TextField("task content", default="")
    has_result = models.BooleanField("has result", default=False)
    result = models.TextField("task result", default="")
    create_time = models.DateTimeField("create_time", default=timezone.now)
    complete_time = models.DateTimeField("create_time", default=timezone.now)
    types = models.CharField(
        "type",
        max_length=30,
        choices=TYPE_CHOICES,
        default="TEST"
    )

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return str(self.uuid)


def generate_token():
    t_uuid = str(uuid.uuid1())
    t_token = hashlib.md5((t_uuid+str(timezone.now())).encode(encoding="utf-8")).digest().hex()
    return t_token


class Token(models.Model):

    id = models.AutoField("ID", primary_key=True)
    key = models.CharField("token", max_length=50, default=generate_token)
    create_time = models.DateTimeField("create_time", default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # name = models.CharField("name", max_length=20, default="")

    def __str__(self):
        return self.key
        return self.key

    def generate_token(self):
        t_uuid = str(uuid.uuid1())
        t_token = hashlib.md5((t_uuid+str(timezone.now())).encode(encoding="utf-8")).digest().hex()
        return t_token

    def refresh_token(self):
        self.key = self.generate_token()
        return self.key
