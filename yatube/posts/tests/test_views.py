import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    """Тест views приложения Posts"""
    username = 'auth'
    group_title = 'Тайтл'
    group_slug = 'group_slug'
    group_description = 'group_description'
    count_page = 1
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )
    image_template = 'posts/small.gif'
    image_name = 'small.gif'
    image_content = 'image/gif'

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
        cls.uploaded = SimpleUploadedFile(
            name=cls.image_name,
            content=cls.small_gif,
            content_type=cls.image_content
        )
        cls.post_any_text = Post.objects.create(
            author=cls.user,
            text='any_text',
            image=cls.uploaded,
            group=cls.group
        )

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        elif post:
            self.assertIn('posts', context)
            post = context['posts']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, PostViewTest.user)
        self.assertEqual(post.pub_date, PostViewTest.post_any_text.pub_date)
        self.assertEqual(post.text, PostViewTest.post_any_text.text)
        self.assertEqual(post.group, PostViewTest.post_any_text.group)
        self.assertEqual(post.image, PostViewTest.post_any_text.image)

    def test_pages_uses_correct_template(self):
        """Проверка: страницы используют верный шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': self.group_slug})
            ): 'posts/group_list.html',
            (
                reverse('posts:profile', kwargs={'username': self.username})
            ): 'posts/profile.html',
            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post_any_text.id}
                )
            ): 'posts/post_detail.html',
            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post_any_text.id}
                )
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_create_show_correct_context(self):
        """Проверка: страница post_create использует
        верный контекст."""
        response = self.authorized.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Проверка: страница post_edit использует
        верный контекст."""
        response = self.authorized.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_any_text.id}
        ))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_show_correct_context(self):
        """Проверка: страница index использует
        верный контекст."""
        post = self.authorized.get(reverse('posts:index'))
        context = post.context
        self.check_context_contains_page_or_post(context, post)

    def test_group_show_correct_context(self):
        post = self.authorized.get(
            reverse('posts:group_list', kwargs={'slug': self.group_slug})
        )
        context = post.context
        self.check_context_contains_page_or_post(context)

    def test_post_detail_show_correct_context(self):
        """Проверка: страница post_detail использует
        верный контекст."""
        response = self.authorized.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post_any_text.id}
            )
        )
        context_post = response.context['posts']
        self.assertEqual(context_post.author, PostViewTest.user)
        self.assertEqual(
            context_post.pub_date, PostViewTest.post_any_text.pub_date
        )
        self.assertEqual(context_post.text, PostViewTest.post_any_text.text)
        self.assertEqual(context_post.group, PostViewTest.post_any_text.group)

    def test_profile_show_correct_context(self):
        """Проверка: страница profile использует
        верный контекст."""
        page = self.authorized.get(
            reverse('posts:profile', kwargs={'username': self.username})
        )
        context = page.context
        self.check_context_contains_page_or_post(context)

    def test_posts_avail_on_pages(self):
        """Проверка: посты доступны на страницах:
        index, group_list, profile."""
        response = self.authorized.get(reverse('posts:index'))
        response_group = response.context.get('post').group.title
        self.assertEqual(response_group, self.group_title)
        response = self.authorized.get(
            reverse('posts:group_list', kwargs={'slug': self.group_slug})
        )
        response_post = response.context.get('post').id
        response_group = response.context.get('post').group.title
        self.assertEqual(response_post, self.post_any_text.id)
        self.assertEqual(response_group, self.group_title)
        response = self.authorized.get(
            reverse('posts:profile', kwargs={'username': self.username})
        )
        for post_ in response.context.get('page_obj'):
            self.assertEqual(post_.id, self.post_any_text.id)
            self.assertEqual(post_.group.title, self.group_title)

    def test_about_uses_correct_template(self):
        """Проверка: страницы используют верный шаблон."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse('about:us'): 'about/us.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_uses_correct_template(self):
        """Проверка: страница использует верный шаблон."""
        templates_url_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_signup_uses_correct_context(self):
        """Проверка: страница использует верный контекст."""
        response = self.client.get(reverse('users:signup'))

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.EmailField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Проверка кеширования главной страницы."""
        response_first = self.client.get(reverse('posts:index'))
        post = Post.objects.get(id=self.post_any_text.id)
        Post.objects.filter(id=self.post_any_text.id).delete()
        response_second = self.authorized.get(reverse('posts:index'))
        self.assertIn(post.text, response_first.content.decode('utf-8'))
        self.assertIn(post.text, response_second.content.decode('utf-8'))
        cache.clear()
        clear_response = self.authorized.get(reverse('posts:index'))
        self.assertNotIn(post.text, clear_response.content.decode('utf-8'))
