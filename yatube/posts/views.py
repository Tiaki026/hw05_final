from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from .utils import paginate
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings


@cache_page(settings.CACHE_TIME, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    context = {
        'posts': posts,
        'page_obj': paginate(request, posts)
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': posts,
        'page_obj': paginate(request, posts)
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    following = (
        request.user.is_authenticated
        and author != request.user
        and Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
    )
    template = 'posts/profile.html'
    context = {
        'author': author,
        'page_obj': paginate(request, posts),
        'posts': posts,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    posts = get_object_or_404(Post, id=post_id)
    template = 'posts/post_detail.html'
    form = CommentForm()
    comments = posts.comments.all()
    context = {
        'posts': posts,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm()
    context: dict = {
        'is_edit': False,
        'form': form
    }
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
        )
    if not form.is_valid():
        return render(request, template, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {

        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return redirect('posts:post_detail', comment_id)
    comment.delete()
    return redirect('posts:post_detail', comment.post.id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related(
        'author',
        'group',
        ).filter(
            author__following__user=request.user
        )
    context = {
        'page_obj': paginate(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(
        User,
        username=username
    )
    if (author.id != request.user.id):
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect('posts:profile', username=username)

# Create your views here.
