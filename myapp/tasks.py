import time
from updater.updater import TaskUpdater
import uuid
from celery import shared_task


@shared_task()
def current_task(**kwargs):
    # some long code
    time.sleep(1)
    # more code


@shared_task()
def new_format_task(task_uuid, task_name):
    updater = TaskUpdater(task_uuid=task_uuid, task_name=task_name, verbose=1)

    with updater(task_name=task_name):
        # here the code
        time.sleep(1)
        # notify something if you want
        updater.notify('Some notification related to the task')
        # more code
        time.sleep(1)
        current_task.delay()

    updater.raise_latest_exception()  # in case of it is needed...


@shared_task()
def new_format_task_1(uuid=uuid.uuid4(), name='TEST', verbose=1):

    updater = TaskUpdater(task_uuid=uuid, task_name=name, verbose=verbose)

    with updater(task_name=name + 'First part'):
        # here some code
        time.sleep(1)
        updater.notify('Some notification related to the task')

    with updater(task_name=name + 'Second part'):
        time.sleep(20)
        my_task_2(updater=updater)

    updater.raise_latest_exception()  # in case of...


@shared_task()
def my_task_2(updater=None):

    with updater(task_name='My subtask 1 in my task 2'):
        # here some code
        time.sleep(1)
        updater.notify('Some notification related to the task')

    with updater(task_name='My subtask 2 in my task 2'):
        time.sleep(10)
        1/0  # raise exception
        updater.notify('Some notification related to the task')

    with updater(task_name='My subtask 3 in my task 2'):
        # here some code
        time.sleep(1)
        updater.notify('Some notification related to the task')
