import datetime
from django.utils.timezone import get_current_timezone
from .models import LogUpdater


class TaskUpdater(object):
    FAIL = 0
    COMPLETED = 1
    PENDING = 2

    def __init__(self, verbose=True, suppress_exception=True,
                 task_uuid=None, task_name=None):
        self.verbose = verbose
        self.task_name = task_name
        self.task_uuid = task_uuid
        self.history = []
        self.exc_history = []
        self._finished = False
        self.suppress_exception = suppress_exception
        self.finished_tasks = []
        self.log_entry = {'log': ""}  # here is where we update changes

        # create log for a specific task
        self.log_obj = LogUpdater.objects.get_or_create(
            task_name=self.task_name,
            task_uuid=self.task_uuid,
            status=2  # PENDING When task starts
        )

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        return self

    def __enter__(self):
        self.start_task(task_name=self.task_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.exc_history.append((exc_type, exc_val, exc_tb))
            self.finish_task(TaskUpdater.FAIL, error=exc_val)
            self.finished_tasks.append(False)
            return self.suppress_exception
        elif not self._finished:
            self.finish_task(TaskUpdater.COMPLETED)
            self.finished_tasks.append(True)
            return True

    def exception_raised(self):
        return len(self.exc_history) > 0

    def raise_latest_exception(self):
        self.insert_final_update()
        if self.exc_history:
            raise self.exc_history[-1][0](
                self.exc_history[-1][1]).with_traceback(
                self.exc_history[-1][2])

    def start_task(self, task_name):
        # for each task or subtask
        self.start_t = datetime.datetime.now(tz=get_current_timezone())
        self._finished = False
        self.task_name = task_name
        self.end_t = None
        self.notify(' - ' + self.task_name)

    def finish_task(self, reason, import_result=None, error=None):
        # for each task or subtask
        self.end_t = datetime.datetime.now(tz=get_current_timezone())
        self._finished = True
        if reason != TaskUpdater.FAIL:
            self.notify('\tSuccessfully completed')
        else:
            self.notify('\tFailed')

        delta = self.end_t - self.start_t
        self.notify('\tTime spent: {0}h{1}m'.format(
            delta.seconds // 3600, (delta.seconds // 60) % 60))
        if reason == TaskUpdater.FAIL:
            self.notify('\tSee error message:\n{}: {}'.format(
                str(type(error)), error))
        elif import_result is not None:
            self.notify('\t{}'.format(str(import_result)))

    def get_final_exception(self):
        return str(self.exc_history[-1][1]) if self.exc_history else ""

    def insert_final_update(self):
        self.update_log(
            end=datetime.datetime.now(tz=get_current_timezone()),
            finished=True,
            status=all(self.finished_tasks),
            exception=self.get_final_exception(),
        )
        self.notify("Task Finished - {} out of {} jobs finished".format(
            sum(self.finished_tasks), len(self.finished_tasks)))

    def notify(self, message):
        msg = '\t' + message
        self.history.append(msg)
        if self.verbose:
            print(msg)
        self.update_log(message=msg + '\n')

    def update_log(self, message=None, end=None, exc_history=None,
                   finished=None, status=None, exception=None, ):
        if message:
            log = self.log_entry.get('log')
            self.log_entry.update({"log": str(log) + str(message)})
        if end:
            self.log_entry.update({"end": end})
        if finished:
            self.log_entry.update({"finished": finished})
        if status is not None:
            self.log_entry.update({"status": status})
        if exception:
            self.log_entry.update({"exception": exception})
        if exc_history:
            self.log_entry.update({"exception_history": exc_history})

        # updating
        try:
            LogUpdater.objects.filter(
                pk=self.log_obj.pk).update(**self.log_entry)
        except Exception as e:
            if self.verbose:
                print(str(e))
