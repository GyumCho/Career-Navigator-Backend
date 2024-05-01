from django.contrib import admin
from django.utils.translation import gettext_lazy as _lazy

from .models import Job, JobBookmark, JobApplication


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper



@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company']
    list_filter = [('company__name', custom_titled_filter(_lazy('Company')))]

@admin.register(JobBookmark)
class JobBookmarkAdmin(admin.ModelAdmin):
    list_display = ['__str__', "user", "job"]

@admin.register(JobApplication)
class JobApplication(admin.ModelAdmin):
    list_display = ['user', 'job', 'applied_date']
