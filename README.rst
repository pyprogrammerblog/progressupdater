#  Progress Updater for Async Task in Celery

In this small project I tried to set de basis for a Progess Updater that actually tracks any task from our system.

## What is the Progress Updater?
- It is an object insert in each task (sync or async) that keeps track of the current task situation or progress.
- It has also an api endpoint to facilitate current status of each task. This can be used by front-end.

## Implementation
It is very easy to use, and it needs few implementation.
It provides a context manager that makes the dirty part for you.


```python
# old format

def current_task(**kwargs):
    # some long code
    time.sleep(1)
    # more code

# new format

def new_format_task(task_uuid, task_name, updater=None):

    # create instance
    updater = updater or TaskUpdater(task_uuid=task_uuid, task_name=task_name, verbose=1)

    # encapsulate the task with the context manager
    with updater(task_name=task_name):
        # here the code
        time.sleep(1)
        # notify something if you want
        updater.notify('Some notification related to the task')
        # more code
        time.sleep(1)

    # finally reraise latest exception if needed or not...
    updater.raise_latest_exception()  # in case of it is needed...
```

With this format we can also follow tasks that call other tasks. The object will follow the flow of the code.

```python
def new_format_task_1(uuid=uuid.uuid4(), name='TEST', verbose=1):

    updater = TaskUpdater(task_uuid=uuid, task_name=name, verbose=verbose)

    with updater(task_name=name + 'First part'):
        # here some code
        time.sleep(1)
        updater.notify('Some notification related to the task')

    with updater(task_name=name + 'Second part'):
        # here we call another method and we make sure we pass the updater
        my_task_2(updater=updater)

    updater.raise_latest_exception()  # in case of...


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
```

The output of the log:

```
	 - TESTFirst part
	Some notification related to the task
		Successfully completed
		Time spent: 0h0m
	 - TESTSecond part
	 - My subtask 1 in my task 2
	Some notification related to the task
		Successfully completed
		Time spent: 0h0m
	 - My subtask 2 in my task 2
		Failed
		Time spent: 0h0m
		See error message:
<class 'ZeroDivisionError'>: division by zero
	 - My subtask 3 in my task 2
	Some notification related to the task
		Successfully completed
		Time spent: 0h0m

	Task Finished - 3 out of 4 jobs finished

```

The api looks like:

```json
    {
        "task_name": "TEST",
        "task_uuid": "54bf5712-b9ec-11e9-afdd-8c16454a0938",
        "start": null,
        "end": "2019-08-08T14:54:12.788631Z",
        "log": "\t - TESTFirst part\n\tSome notification related to the task\n\t\tSuccessfully completed\n\t\tTime spent: 0h0m\n\t - TESTSecond part\n\t - My subtask 1 in my task 2\n\tSome notification related to the task\n\t\tSuccessfully completed\n\t\tTime spent: 0h0m\n\t - My subtask 2 in my task 2\n\t\tFailed\n\t\tTime spent: 0h0m\n\t\tSee error message:\n<class 'ZeroDivisionError'>: division by zero\n\t - My subtask 3 in my task 2\n\tSome notification related to the task\n\t\tSuccessfully completed\n\t\tTime spent: 0h0m\n\tTask Finished - 3 out of 4 jobs finished\n",
        "exception": "division by zero",
        "finished": true,
        "status": 0
    }
```