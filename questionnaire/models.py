from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _lazy

class QuestionResult(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    MbtiType = models.CharField(max_length=250, default="")
    codeOne = models.CharField(max_length=250,  default="")
    codeTwo = models.CharField(max_length=250,  default="", blank=True)
    category_one = models.CharField(max_length=250,  default="")
    category_two= models.CharField(max_length=250,  default="")  
    category_three = models.CharField(max_length=250,  default="")

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = _lazy("question result")
        verbose_name_plural = _lazy("question results")
