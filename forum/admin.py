from django.contrib import admin

from .models import Category, Comment, Page


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = (('category__name', custom_titled_filter('Category')),)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_short', 'page', 'created_at', 'owner')

    def get_short(self, obj):
        if len(obj.description) <= 24:
            return obj.description
        return f"{obj.description[:24]}..."
    get_short.short_description = "description"
