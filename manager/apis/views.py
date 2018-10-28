from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from web.models import ConfigFile, Agent, Task, Token
from web import msgq
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED
)
from rest_framework.response import Response
from rest_framework import viewsets
from . import serializers
import json


task_queue = msgq.MessageQ()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer


class ConfigViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authenticated users to view or edit config files.
    """
    queryset = ConfigFile.objects.all()
    serializer_class = serializers.ConfigSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authenticated users to view or edit agent.
    """
    queryset = Agent.objects.all()
    serializer_class = serializers.AgentSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows authenticated users to view or edit tasks.
    """
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    """
    API endpoint that allow user to get token using username and passwords, if no token exist, create one for the user
    :param request: django http request
    :return: response with token if succeeded
    """
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'detail': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'detail': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    try:
        token = Token.objects.all().filter(user=user)[0]
    except IndexError:
        token = Token.objects.create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def create_new_task(request):
    """
    create a new task(TEST, GET, or POST), and return the task id
    :param request: django http request
    :return: response with task id if succeeded
    """
    task_data = request.body
    print(task_data)
    try:
        task_data = json.loads(task_data.decode("utf-8"))
    except json.decoder.JSONDecodeError:
        return Response({'detail': 'JSON decode error'}, status=HTTP_400_BAD_REQUEST)
    task_id = task_queue.push_task(task_data)
    return Response({'id': task_id}, status=HTTP_201_CREATED)
