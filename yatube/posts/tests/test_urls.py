from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    """Тест urls приложения posts
    setUpClass - фикстура."""
    group_title = 'Тайтл'
    group_slug = 'group_slug'
    group_description = 'group_description'
    username = 'auth'
    post_text_first = 'Текст'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.username)
        cls.authorized = Client()
        cls.authorized.force_login(cls.user)
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug=cls.group_slug,
            description=cls.group_description
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.post_text_first,
            group=cls.group,
        )

    def test_urls_autorized(self):
        """Проверка доступности шаблонов авторизованному
        пользователю."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/group_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_unautorized(self):
        """Проверка доступности шаблонов неавторизированному
        пользователю."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/group_slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect(self):
        """Проверка редиректов для навторизированного
        пользователя."""
        response = self.client.get('/create/')
        self.assertRedirects(response, ('/auth/login/?next=/create/'))
        response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{self.post.id}/edit/')
        )

    def test_page_not_found(self):
        """Проверка недоступности несуществующих страниц."""
        response = self.client.get('posts/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_about(self):
        """Проверка доступности адресов по шаблонам.
        Проверка: страница использует верный шаблон."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
            'about/us.html': '/about/us/',
        }

        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_about(self):
        """Проверка доступности адресов неавторизированному
        пользователю."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect(self):
        """Проверка редиректа неавторизированного пользователя."""
        request = self.client.get('/auth/password_change/done/')
        self.assertRedirects(request, (
            '/auth/login/?next=/auth/password_change/done/'
        ))
        request = self.client.get('/auth/password_change/')
        self.assertRedirects(request, (
            '/auth/login/?next=/auth/password_change/'
        ))

    def test_comment_unauthorized(self):
        """Проверка редиректа неавторизированного пользователя."""
        request = self.client.get(f'/posts/{self.post.id}/comment/')
        self.assertEqual(request.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            request, (f'/auth/login/?next=%2Fposts%2F'
                      f'{self.post.id}%2Fcomment%2F')
        )
