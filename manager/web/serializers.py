from rest_framework import serializers
from .models import ConfigFile, Agent
from django.contrib.auth.models import User


class ConfigSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfigFile
        fields = "__all__"


class ConfigSerializerForAgent(serializers.ModelSerializer):

    class Meta:
        model = ConfigFile
        fields = ("name", "id", "path")


class AgentSerializer(serializers.ModelSerializer):

    configs = ConfigSerializerForAgent(many=True, read_only=True)

    class Meta:
        model = Agent
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("username", "password", "email", "id")
