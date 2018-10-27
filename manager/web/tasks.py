from background_task import background
from . import models
from . import msgq
from logging import getLogger
from manager import const

logger = getLogger(__name__)
message_queue = msgq.MessageQ()


def test_task():
    """
    test task
    :return: None
    """
    logger.debug("task test")


def get_results_from_message_queue():
    """
    task for getting all results from message queue
    :return: None
    """
    message_queue.get_result_length()
    logger.info("get task results from task queue")


def test_all_servers_connection():
    """
    task for testing all servers' connection status
    :return: None
    """
    task_data = dict(const.TEST_TASK)
    task_data["client_list"] = list()
    agents = models.Agent.objects.all()
    for agent in agents:
        task_data["client_list"].append({"id": agent.id, "ip_address": agent.ip_address})
    message_queue.push_task(task_data)
    logger.info("create tasks to test all agents' connection status")


def start_task():
    """
    start repeat tasks above
    :return: None
    """
    get_results_from_message_queue()
    test_all_servers_connection()
