# encoding=utf-8
import ast
from celery import current_app
from user_agents import parse


def resend_failed_task(task, filtered_user=[]):
    """
    重发数据库中记录的失败的任务
    :param task: djcelery.models.TaskState instance
    :param filtered_user:过滤的用户id列表[123, 4456]
    :return:
    """
    task_args = ast.literal_eval(task.args)
    task_kwargs = ast.literal_eval(task.kwargs)
    if task_kwargs.get('user_id') in filtered_user:
        return
    task_name = task.name
    current_app.send_task(task_name, args=task_args, kwargs=task_kwargs)


def utype_is_mobile(request):
    is_mobile = False
    ua = request.META.get('HTTP_USER_AGENT', '')
    if ua:
        user_agent = parse()
        if user_agent.is_mobile:
            is_mobile = True

    return is_mobile
