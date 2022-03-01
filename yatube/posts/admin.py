"""Модуль настройки администратоской панели admin.py"""

from django.contrib import admin

from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    """PostAdmin - метакласс, добавляет функционал админ-панели.
    list_display - перечисляет поля, которые должны отображаться в админке.
    search_fields - добавляет интерфейс поиска по тексту постов.
    list_filter - Добавляет возможность фильтрации по дате.
    """
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
