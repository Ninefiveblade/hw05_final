"""Модуль обработки адресов posts/views.py"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Post, Follow, Group, User
from .forms import PostForm, CommentForm
from .utils import paginator_obg
from django.views.decorators.cache import cache_page
from django.conf import settings


@cache_page(settings.CACHE_INDEX_TIME)
def index(request):
    """Функция index определяет свойства главной страницы.
    template - путь файла html главной страницы,
    posts - выводит 10 постов на странице,
    context - передает словарь в файл html.
    """
    template_name = 'posts/index.html'
    title = "Это главная страница проекта Yatube"
    post_list = Post.objects.all()
    page_obj = paginator_obg(request, post_list)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


def group_posts(request, slug):
    """Функция group_posts определяет свойства страницы cообществ.
    template - путь файла html страницы сообществ,
    posts - выводит 10 постов на странице,
    group - возвращает сообщение об ошибке, если объект не найден.
    context - передает словарь в файл html.
    """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.all()
    page_obj = paginator_obg(request, posts)
    context = {
        'title': 'Группы',
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """Вью-функция страницы поста.
    user - получение пользователя из User.
    posts - фильтр постов по user.
    """
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    page_obj = paginator_obg(request, posts)
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=user).exists()
    else:
        following = False
    context = {
        'author': user,
        'count': posts.count(),
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Вью-функция страницы поста.
    posts - получение поста по id.
    author - получение имени влдаельца поста.
    title - получение 30 символов из поста в tittle.
    count - подсчет постов автора.
    """
    form = CommentForm()
    posts = Post.objects.get(id=post_id)
    author = posts.author
    title = f'{posts.text[:30]}'
    count = Post.objects.filter(author=posts.author).count()
    context = {
        'title': title,
        'posts': posts,
        'author': author,
        'count': count,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Вью-функция создания поста.
    form - форма с пост методом
    post.author - автор сохраненного поста -
    form.save
    В случае валидации формы и успешной отпавляется
    На страницу profile, с post.author.id
    """
    title = 'Новый пост'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form.cleaned_data['text']
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    form = PostForm(request.POST)
    context = {
        'title': title,
        'form': form
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Вью-функция редактирования поста.
    post - получаем редактируемый пост,
    author получаем пользователя из запроса,
    form - инициализируем форму редактируемым постом.
    """
    title = 'Редактирование поста'
    post = Post.objects.get(id=post_id)
    author = request.user
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if author.id != post.author.id:
        return redirect('posts:post_detail', post.id)
    elif author.id == post.author.id and form.is_valid():
        form.save()
        return redirect('posts:post_edit', post.id)
    context = {
        'title': title,
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    print(form.errors)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Функция отображения постов, на которые
    подписан пользователь."""
    template_name = 'posts/follow.html'
    title = "Страница постов с подписками"
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_obg(request, posts)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


@login_required
def profile_follow(request, username):
    """Функция подписки на автора."""
    author = get_object_or_404(User, username=username)
    check_follow = Follow.objects.filter(
        author=author, user=request.user
    ).exists()
    if not check_follow and request.user != author:
        request.user.follower.create(author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Функция отписки от автора."""
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect('posts:index')
