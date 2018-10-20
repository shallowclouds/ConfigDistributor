from django.contrib.auth.models import User
from rest_framework import serializers
from web.models import ConfigFile, Agent, Task


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', )


class ConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ConfigFile
        fields = "__all__"


class AgentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"
