import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from ..models import Group, Post, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostsForms(TestCase):
    """Тест views приложения about"""
    username = 'auth'
    username_follower = 'follower'
    group_title = 'Тайтл'
    group_slug = 'slug'
    group_description = 'group_description'
    post_text = 'Текст'
    post_id = 1
    post_text_second = 'Текст2'
    post_id_second = 2
    counter_user_create = 3
    counter_follow = 3
    counter_posts = 2
    follow_object_id = 1
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
    second_image_name = 'pixel.gif'
    second_image_template = 'posts/pixel.gif'
    comment_text = 'comment_text'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=cls.username)
        cls.user_follower = User.objects.create_user(
            username=cls.username_follower
        )
        cls.authorized = Client()
        cls.follower = Client()
        cls.authorized.force_login(cls.user)
        cls.follower.force_login(cls.user_follower)
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

        cls.uploaded_second = SimpleUploadedFile(
            name=cls.second_image_name,
            content=cls.small_gif,
            content_type=cls.image_content
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text=cls.post_text,
            group=cls.group,
            id=cls.post_id
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create_in_database(self):
        """Проверка создания поста в базе данных."""
        form_data = {
            'text': self.post_text_second,
            'group': self.group.id,
            'image': self.uploaded
        }
        self.authorized.post(reverse('posts:post_create'), data=form_data)
        count_post = Post.objects.all().count()
        self.assertEqual(count_post, self.counter_posts)
        self.assertTrue(
            Post.objects.filter(
                text=self.post_text_second,
                image=self.image_template,
                author=self.user,
                group=self.group.id,
                id=self.post_id_second
            ).exists()
        )

    def test_post_edit_database_correct(self):
        """Проверка корректного изменения
        поста в базе данных."""
        form_data = {
            'text': self.post_text_second,
            'image': self.uploaded_second
        }
        self.authorized.post(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_id}), form_data,
        )
        self.assertTrue(
            Post.objects.filter(
                text=self.post_text_second,
                image=self.second_image_template,
                author=self.user,
                id=self.post_id,
                group=None
            ).exists()
        )

    def test_create_user(self):
        """Проверка создания нового пользователя."""
        form_signup = {
            'first_name': 'Иван',
            'last_name': 'Алексеев',
            'username': 'lexeone',
            'email': 'cherep1.92@mail.ru',
            'password1': 'Sp135246',
            'password2': 'Sp135246',
        }
        self.assertIsInstance('users:signup', str)
        self.client.post(reverse('users:signup'), form_signup)
        self.assertEqual(User.objects.all().count(), self.counter_user_create)

    def test_comment_create(self):
        """Проверка создания комментов."""
        Comment.objects.create(
            post=self.post,
            text=self.comment_text,
            author=self.user
        )
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                text=self.comment_text,
                author=self.user
            )
        )

    def test_follow_created_deleted(self):
        """Проверка отпииски и подписки на автора."""
        self.user_follower.follower.create(author=self.user)
        object_follow = Follow.objects.get(id=self.follow_object_id)
        post = Post.objects.get(author=self.user.id)
        follow = self.follower.get(
            reverse('posts:follow_index')
        ).context['post']
        unfollow = self.authorized.get(reverse('posts:follow_index'))
        self.assertEqual(object_follow.author, post.author)
        self.assertEqual(object_follow.user, self.user_follower)
        self.assertEqual(post, follow)
        self.assertNotIn(post.text, unfollow.content.decode('utf-8'))
        self.user.following.filter(user=self.user_follower).delete()
        self.assertFalse(Follow.objects.filter(
            id=self.follow_object_id).exists()
        )
