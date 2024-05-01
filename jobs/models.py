from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _lazy
from martor.models import MartorField
from core.models import Company


class Job(models.Model):
    title = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    location = models.CharField(max_length=100)
    description = MartorField(max_length=500)
    requirements = models.CharField(max_length=500)
    salary = models.CharField(max_length=50) # text for now
    instructions = models.CharField(max_length=500)
    deadline = models.DateField()
    keywords = models.CharField(max_length=100)
    image = models.URLField(max_length=100)
    contact_info = models.CharField(max_length=500)
    mbti = models.CharField(max_length=500)
    job_fields = models.CharField(max_length=500)
    holland = models.CharField(max_length=500)
    additional = models.CharField(max_length=500)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = _lazy("job")
        verbose_name_plural = _lazy("jobs")

class JobApplication(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    job = models.ForeignKey(Job, on_delete=models.PROTECT)
    applied_date = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    interviewed = models.BooleanField(default=False)
    tested = models.BooleanField(default=False)
    feedback = models.TextField('feedback', blank=True, default="")

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','job'],name="jaconstraint")]
        verbose_name = _lazy("job application")
        verbose_name_plural = _lazy("job applications")

class JobBookmark(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    job = models.ForeignKey(Job, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','job'],name="bconstraint")]
        verbose_name = _lazy("job bookmark")
        verbose_name_plural = _lazy("job bookmarks")

    def __str__(self) -> str:
        return f'{self.user.get_username()} - {self.job.title}'
