from django.contrib.auth.models import User
from rest_framework import serializers
from web.models import ConfigFile, Agent, Task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', )


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigFile
        fields = "__all__"


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
