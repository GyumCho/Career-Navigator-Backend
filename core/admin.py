from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _lazy, gettext as _

from .models import User, Company, FailedLogin, Tip

def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_mentor")

    fieldsets = (
        *DjangoUserAdmin.fieldsets[0:2],
        (_lazy("CareerNavigator info"), {"fields": ("is_jobseeker", "is_mentor", "employer", "mentor","complete_question", "education","work_experience","contact","interest","skill","others","motivation1","motivation2","motivation3","short_goal","long_goal","resume_pdf")}),
        *DjangoUserAdmin.fieldsets[2:],
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
        (
            _lazy("CareerNavigator info"),
            {
                "fields": ("is_jobseeker", "is_mentor", "employer", "mentor"),
            }
        )
    )
    list_filter = [
        *DjangoUserAdmin.list_filter,
        ('is_jobseeker', custom_titled_filter(_lazy("jobseeker status"))),
        ('is_mentor', custom_titled_filter(_lazy("mentor status"))),
        ('employer__name', custom_titled_filter(_lazy("employer"))),
    ]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(FailedLogin)
class FailedLoginAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'updated_at', 'attempts')

@admin.register(Tip)
class Tip(admin.ModelAdmin):
    list_display = ("description", "url")
