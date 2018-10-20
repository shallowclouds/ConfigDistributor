from django.contrib.auth.models import User
from web.models import ConfigFile, Agent, Task
from rest_framework import viewsets
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer


class ConfigViewSet(viewsets.ModelViewSet):
    queryset = ConfigFile.objects.all()
    serializer_class = serializers.ConfigSerializer


class AgentViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = serializers.AgentSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
