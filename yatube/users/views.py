"""Модуль обработки адресов users/views.py"""
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm


class SignUp(CreateView):
    """Класс SignUp - обработчик данных страницы регистрации.
    form_class - объект формы
    template_name - путь к шаблону
    success_url - переадресация в случае успеха."""
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
