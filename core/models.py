import datetime
import ipaddress
from typing_extensions import Self, Optional

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _lazy
from django.utils import timezone

from martor.models import MartorField

class Tip(models.Model):
    description = models.TextField('description', blank=True)
    url = models.URLField(max_length=200)

    class Meta:
        verbose_name = _lazy("tip")
        verbose_name_plural = _lazy("tips")

class Company(models.Model):
    name = models.CharField(max_length=64)
    description = MartorField(max_length=500)
    slug = models.SlugField(max_length=32)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _lazy('company')
        verbose_name_plural = _lazy("companies")

def upload_to_path(instance: AbstractUser, filename: str) -> str:
    return f"api/pdf/{instance.username}/{filename}"

class User(AbstractUser):
    is_jobseeker: bool = models.BooleanField(default=True)
    is_mentor: bool = models.BooleanField(default=False)
    employer: Optional[Company] = models.ForeignKey(Company, on_delete=models.PROTECT, default=None, blank=True, null=True, related_name='employee_set')
    education = models.JSONField('Education', default=list, blank=True)
    work_experience = models.JSONField('Work_Experience', default=list, blank=True)
    contact = models.JSONField('contact', default=list, blank=True)
    interest = models.TextField(blank=True, verbose_name='interest')
    skill = models.TextField(blank=True, verbose_name='skill')
    others = models.TextField('others', blank=True)
    motivation1 = models.TextField('motivation1', blank=True)
    motivation2 = models.TextField('motivation2', blank=True)
    motivation3 = models.TextField('motivation3', blank=True)
    short_goal = models.TextField('short_goal', blank=True)
    long_goal = models.TextField('long_goal', blank=True)
    resume_pdf = models.FileField(upload_to=upload_to_path, null=True, blank=True)
    complete_question = models.BooleanField(default=False)
    mentor = models.ForeignKey('user', null=True, blank=True, on_delete=models.PROTECT, related_name='mentee_set')

    class Meta:
        verbose_name = _lazy("user")
        verbose_name_plural = _lazy("users")
    
def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class FailedLogin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(unique=True)
    attempts = models.IntegerField(default=1)

    @classmethod
    def report_failure(cls, request: HttpRequest, failure: Optional[Self]=None) -> int:
        if failure:
            if failure.updated_at < (timezone.now() - datetime.timedelta(hours=1)):
                failure.attempts = 1
            else:
                failure.attempts += 1
            failure.save()
            return failure.attempts

        host = get_client_ip(request)
        ip = ipaddress.ip_address(host)

        if isinstance(ip, ipaddress.IPv6Address):
            ip = ipaddress.IPv6Address(bytes([*ip.packed[:8], *([0]*8)]))
        
        try:
            obj = cls.objects.get(ip_address=str(ip))
            if obj.updated_at < (timezone.now() - datetime.timedelta(hours=1)):
                obj.attempts = 1
            else:
                obj.attempts += 1
            obj.save()
            return obj.attempts
        except cls.DoesNotExist:
            return cls.objects.create(ip_address=str(ip)).attempts

    @classmethod
    async def areport_failure(cls, request: HttpRequest, failure: Optional[Self]=None) -> int:
        if failure:
            if failure.updated_at < (timezone.now() - datetime.timedelta(hours=1)):
                failure.attempts = 1
            else:
                failure.attempts += 1
            await failure.asave()
            return failure.attempts

        host = get_client_ip(request)
        ip = ipaddress.ip_address(host)

        if isinstance(ip, ipaddress.IPv6Address):
            ip = ipaddress.IPv6Address(bytes([*ip.packed[:8], *([0]*8)]))
        
        try:
            obj = await cls.objects.aget(ip_address=str(ip))
            if obj.updated_at < (timezone.now() - datetime.timedelta(hours=1)):
                obj.attempts = 1
            else:
                obj.attempts += 1
            await obj.asave()
            return obj.attempts
        except cls.DoesNotExist:
            return (await cls.objects.acreate(ip_address=str(ip))).attempts
    
    @classmethod
    def is_blocked(cls, request: HttpRequest) -> bool:
        host = get_client_ip(request)
        ip = ipaddress.ip_address(host)

        if isinstance(ip, ipaddress.IPv6Address):
            ip = ipaddress.IPv6Address(bytes([*ip.packed[:8], *([0]*8)]))
        
        try:
            obj = cls.objects.get(ip_address=str(ip))
            if obj.updated_at < (timezone.now() - datetime.timedelta(hours=1)):
                return False
            if obj.attempts > 10:
                obj.attempts += 1
                obj.save()
                return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    async def ais_blocked(cls, request: HttpRequest) -> bool:
        host = get_client_ip(request)
        ip = ipaddress.ip_address(host)

        if isinstance(ip, ipaddress.IPv6Address):
            ip = ipaddress.IPv6Address(bytes([*ip.packed[:8], *([0]*8)]))
        
        try:
            obj = await cls.objects.aget(ip_address=str(ip))
            if obj.updated_at < (timezone.now() - datetime.timedelta(hours=1)):
                return False
            if obj.attempts > 10:
                obj.attempts += 1
                await obj.asave()
                return True
        except cls.DoesNotExist:
            return False
    
    class Meta:
        verbose_name = _lazy("failed login")
        verbose_name_plural = _lazy("failed logins")
