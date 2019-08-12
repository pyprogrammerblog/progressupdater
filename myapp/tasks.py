import time
from updater.updater import ProgressUpdater, progress_updater
from celery import task



@task()
def current_task(**kwargs):
    # some long code
    time.sleep(1)
    # more code


@task()
def new_format_task():
    updater = ProgressUpdater(verbose=1)
    with updater():  # if no task_name is passed, the name of the celery task is taken
        # here the code
        time.sleep(1)
        # more code
    updater.raise_latest_exception()  # in case of it is needed...


@task()
@progress_updater
def new_format_task(updater):
    # here the code
    time.sleep(1)
    updater.notify('Some notification related to the task')
    # more code
    updater.notify('More notifications related to the task')

@task()
def new_format_task_1():
    updater = ProgressUpdater(verbose=True)

    with updater(task_name='TEST - First part in new format task'):
        # here some code
        time.sleep(1)
        updater.notify('Some notification related to the task')

    with updater(task_name='TEST - Second part in new format task'):
        time.sleep(20)
        my_task_2(updater=updater)

    updater.raise_latest_exception()  # in case of...


@task()
def my_task_2(updater=None):
    updater = updater or ProgressUpdater(verbose=True)

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


@task()
@progress_updater(task_name='Test 3')
def new_format_task_3(updater):
    # here the code
    updater.notify('Some notification related to the task')
    time.sleep(3)
    1/0
    updater.notify('We do not get this point')
    # more code
