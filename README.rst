Progress Updater for Tasks. The Magic of the Context Managers in Python
=======================================================================

In this small project I tried to set de basis for a ProgessUpdater that tracks any task.

What is the Progress Updater?
-----------------------------
- It is an object inserted in each task (sync or async) that keeps track of the current task situation or progress.
- It has also an api endpoint to facilitate current status retrieving of each task.
  This can be used by front-end apps in order to keep clients updated.

Implementation
-----------------------------
It is very easy to use, and it needs few implementation.
It provides a context manager that makes the dirty part for you. The old format::

    @task()
    def my_task(**kwargs):
        # some long code
        time.sleep(1)
        # more code

The new format::

    @task()
    def my_task(updater=None):

        updater = updater or ProgressUpdater(verbose=1)

        with updater():
            # some long code
            time.sleep(1)
            updater.notify('Some notification related to the task')
            # more code

        updater.raise_latest_exception()  # raise exception if needed...

The easiest and fastest way is to just decorate the method.
It will instantiate the ProgressUpdater and it will do the whole thing for you::

    @task()
    @progress_updater
    def current_task(**kwargs):
        # some long code
        time.sleep(1)
        # more code


With this format we can also follow tasks that call other tasks. The object will follow the flow of the code.::

	def new_format_task_1(task_name='TEST', verbose=1):

	    updater = ProgressUpdater(task_name=task_name, verbose=verbose)

	    with updater(task_name=task_name + ' - First part'):
            # here some code
            time.sleep(1)
            updater.notify('Some notification related to the task')

        with updater(task_name=task_name + ' - Second part'):
            my_task_2(updater=updater)

        updater.insert_final_update()  # ...or raise_latest_exception


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


The output of the log.::

		 - TEST - First part
		    Some notification related to the task
			Successfully completed
			Time spent: 0h0m
		 - TEST - Second part
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


The api looks like.::

	    {
            "task_name": "TEST",
            "task_uuid": "54bf5712-b9ec-11e9-afdd-8c16454a0938",
            "start": "2019-08-08T14:54:10.788631Z",
            "end": "2019-08-08T14:54:12.788631Z",
            "log": "\t - TESTFirst part\n\tSome notification related to the task\n\t\tSuccessfully completed\n\t\tTime spent: 0h0m\n\t - TESTSecond part\n\t - My subtask 1 in my task 2\n\tSome notification related to the task\n\t\tSuccessfully completed\n\t\tTime spent: 0h0m\n\t - My subtask 2 in my task 2\n\t\tFailed\n\t\tTime spent: 0h0m\n\t\tSee error message:\n<class 'ZeroDivisionError'>: division by zero\n\t - My subtask 3 in my task 2\n\tSome notification related to the task\n\t\tSuccessfully completed\n\t\tTime spent: 0h0m\n\tTask Finished - 3 out of 4 jobs finished\n",
            "exception": "division by zero",
            "finished": true,
            "status": 0
	    }

So that is all, basically two things:

1. Make sure you encapsulate with the `updater` context manager the code you want to track.
2. Remember to call `insert_final_update` to write the balance of jobs finished and final statusof the task.
2. Remember to `raise_latest_exception` in case those are need by downstream process.

The admin implement a nice package to export logs in any format, those could be sent monthly to clients with failed task.


The Celery Implementation
-------------------------
The updater in his constructor access to the uuid of the task and the name. Then it generates a log with this task_uuid and task_name.
Run in a terminal.::

    celery --app=progressupdater.celery:app worker --loglevel=INFO

And then open a django shell session and run a task.::

    >>> from myapp.tasks import new_format_task
    >>> new_format_task.delay()
         - myapp.tasks.new_format_task
            Successfully completed
            Time spent: 0h0m
        Task Finished - 1 out of 1 jobs finished


