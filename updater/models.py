from django.db import models


# Create your models here.
class LogUpdater(models.Model):

    status_choices = (
        (0, "FAIL"),
        (1, "COMPLETED"),
        (2, "PENDING")
    )
    task_name = models.CharField(
        max_length=120, help_text='Task name',
    )
    task_uuid = models.UUIDField(
        help_text='Universally unique identifier for task',
        blank=True, null=True
    )
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)
    log = models.TextField(default="")
    exception = models.TextField(default="")
    finished = models.BooleanField(default=False)
    status = models.IntegerField(default=0, choices=status_choices)

    def __str__(self):
        return f"Log for: {self.task_name} - {self.task_uuid}"
