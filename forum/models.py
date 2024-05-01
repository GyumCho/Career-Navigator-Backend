from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from martor.models import MartorField


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name_plural = _lazy("Categories")


class Page(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    title = models.CharField(max_length=64)
    description = MartorField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title}"

    class Meta:
        ordering = ('created_at',)


class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.PROTECT)
    owner = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    description = MartorField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)
