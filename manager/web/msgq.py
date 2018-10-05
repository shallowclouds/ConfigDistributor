from django.conf import settings
import uuid
import redis
from . import models
import json
import logging
import base64
logger = logging.getLogger(__name__)


class MessageQ(object):

    def __init__(self):
        self.queue = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT
            )

    def get_results(self):
        while self.get_task_length() >= 1:
            try:
                result = self.queue.blpop("result")
                objects = json.loads(result[1])
                if objects["type"] == "GET":
                    for idx in range(len(objects["result_list"])):
                        objects["result_list"][idx]["file_content_b64"] = base64.decode(objects["result_list"][idx]["file_content_b64"])
                tuuid = objects["uuid"]
                task = models.Task.objects.all().get(uuid=tuuid)
                task.result = json.dumps(objects)
                task.has_result = True
                task.save()
            except Exception as e:
                logger.error("error occured while getting task results:", e)

    def push_task(self, task):
        tuuid = uuid.uuid1()
        task["uuid"] = str(tuuid)
        content = json.dumps(task)
        ttask = models.Task.objects.create(
            uuid=tuuid,
            task=content,
            types=task["type"]
            )
        if task["type"] == "GET":
            pass
        elif task["type"] == "POST":
            for idx in range(len(task["file_list"])):
                task["file_list"][idx]["file_content_b64"] = base64.encode(
                    task["file_list"][idx]["file_content_b64"]
                    )
        elif task["type"] == "TEST":
            pass
        self.queue.lpush("task", json.dumps(task))
        return ttask.id

    def get_task_length(self):
        return self.queue.llen("task")
