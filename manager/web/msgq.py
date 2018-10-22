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
        while self.get_result_length() > 0:
            try:
                result = self.queue.blpop("result")
                objects = json.loads(result[1])
                if objects["type"] == "GET":
                    for idx in range(len(objects["result_list"])):
                        if not objects["result_list"][idx]["result"]:
                            continue
                        for idx2 in range(len(objects["result_list"][idx]["file_list"])):
                            if not objects["result_list"][idx]["file_list"][idx2]["result"]:
                                continue
                            objects["result_list"][idx]["file_list"][idx2]["file_content_b64"] = base64.b64decode(objects["result_list"][idx]["file_list"][idx2]["file_content_b64"]).decode("utf-8")
                elif objects["type"] == "TEST":
                    objects["result_list"].sort(key=lambda x: x["id"])
                    for result in objects["result_list"]:
                        try:
                            cur_agent = models.Agent.objects.all().get(id=result["id"])
                        except models.Agent.DoesNotExist:
                            continue
                        if result["result"]:
                            cur_agent.status = "Connected"
                        else:
                            cur_agent.status = "Disconnected"
                        cur_agent.save()
                t_uuid = objects["uuid"]
                task = models.Task.objects.all().get(uuid=t_uuid)
                task.result = json.dumps(objects)
                task.has_result = True
                task.save()
            except Exception as e:
                logger.error("error occurred while getting task results:\n", e)

    def push_task(self, task):
        t_uuid = uuid.uuid1()
        print(task)
        task["uuid"] = str(t_uuid)
        content = json.dumps(task)
        t_task = models.Task.objects.create(
            uuid=t_uuid,
            task=content,
            types=task["type"]
            )
        if task["type"] == "GET":
            pass
        elif task["type"] == "POST":
            for idx in range(len(task["file_list"])):
                task["file_list"][idx]["file_content_b64"] = base64.b64encode(
                    bytes(
                        task["file_list"][idx]["file_content_b64"],
                        encoding="utf8")
                    ).decode("ascii")
        elif task["type"] == "TEST":
            pass
        self.queue.lpush("task", json.dumps(task))
        return t_task.id

    def get_task_length(self):
        return self.queue.llen("task")

    def get_result_length(self):
        return self.queue.llen("result")
