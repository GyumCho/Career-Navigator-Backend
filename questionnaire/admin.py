from django.contrib import admin

from .models import QuestionResult


@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    list_display = ("user", "MbtiType", "codeOne","codeTwo","category_one","category_two","category_three")
