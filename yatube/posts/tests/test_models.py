from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    "Тест models приложения posts"
    group_title = 'Тестовая группа'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=cls.group_title,
        )
        cls.post_test_message = Post.objects.create(
            author=cls.user,
            text='test_message',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post_test_message
        text = post.text[:15]
        self.assertEqual(text, str(post))
        group = PostModelTest.group
        title = group.title
        self.assertEqual(title, str(group))

    def test_models_have_verbose_name(self):
        """Проверяем есть ли у моделей verbose_name"""
        post = PostModelTest.post_test_message
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_models_have_verbose_name(self):
        """Проверяем есть ли у моделей help_text"""
        post = PostModelTest.post_test_message
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
