from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from posts.models import Post, Group


User = get_user_model()


class PaginatorViewsTest(TestCase):
    """Тест паджинатора приложения posts"""
    group_title = 'Тайтл'
    group_slug = 'group_slug'
    group_description = 'group_description'
    username = 'auth'
    counter_iter = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unautorized = Client()
        cls.user = User.objects.create_user(username=cls.username)
        cls.authorized = Client()
        cls.authorized.force_login(cls.user)
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug=cls.group_slug,
            description=cls.group_description
        )
        for i in range(cls.counter_iter):
            Post.objects.create(
                author=cls.user,
                text=i,
                group=cls.group,
                id=i
            )

    def test_first_page_contains_ten_records(self):
        """Проверка: index содержит 10 постов на 1 странице"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), settings.PAGE_COUNTER_TEN
        )

    def test_second_page_contains_three_records(self):
        """Проверка: index содержит 3 поста на 2 странице"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        remaining_posts = (
            Post.objects.all().count() - settings.PAGE_COUNTER_TEN
        )
        self.assertEqual(len(response.context['page_obj']), remaining_posts)

    def test_first_page_contains_ten_records_group(self):
        """Проверка: group_list содержит 10 постов на 1 странице"""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_slug})
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.PAGE_COUNTER_TEN
        )

    def test_second_page_contains_ten_records_group(self):
        """Проверка: group_list содержит 3 поста на 2 странице"""
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group_slug}
            ) + '?page=2'
        )
        remaining_posts = (
            Post.objects.all().count() - settings.PAGE_COUNTER_TEN
        )
        self.assertEqual(len(response.context['page_obj']), remaining_posts)

    def test_first_page_contains_ten_records_profile(self):
        """Проверка: profile содержит 10 постов на 1 странице"""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.username})
        )
        self.assertEqual(
            len(response.context['page_obj']), settings.PAGE_COUNTER_TEN
        )

    def test_second_page_contains_ten_records_profile(self):
        """Проверка: profile содержит 3 поста на 2 странице"""
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': self.username}
            ) + '?page=2'
        )
        remaining_posts = (
            Post.objects.all().count() - settings.PAGE_COUNTER_TEN
        )
        self.assertEqual(len(response.context['page_obj']), remaining_posts)
