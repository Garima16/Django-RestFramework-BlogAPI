from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Post
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from django.db.models import Q
from django.conf import settings
from django import http
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from accounts.views import login_view


class BlockedIPMiddleware(object):
    def process_request(self, request):
        if request.META['REMOTE_ADDR'] in settings.BLOCKED_IPS:
            return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        return None

"""
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog:blog.views.post_detail', pk=post.pk)
    else:
        form = CommentForm()
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'blog/comments.html', context)
"""


def post_list(request):
    if not request.user.is_authenticated():
        return redirect('accounts.views.login_view')
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

    #search code starts

    query = request.GET.get("q")
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(text__icontains=query)
        ).distinct()

    #ends

    #pagination code part

    paginator = Paginator(posts, 3)#display 4 posts on a page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)


    #ends

    context = {
        #'posts': posts,#for search
        'queryset': queryset,#for displaying posts
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    if not request.user.is_authenticated():
        return render(request, 'blog/login.html')
    else:
        user = request.user
        post = get_object_or_404(Post, pk=pk)
        read_time = post.get_read_time()
        post.read_time = read_time
        wc = post.count_words()
        post.word_count = wc
        """
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        """
        context = {
            'post': post,
            'user': user,
            #'parent' : parent_obj
        }
        return render(request, 'blog/post_detail.html', context)


def mypost_list(request):
    if not request.user.is_authenticated():
        return render(request, 'blog/login.html')
    posts = Post.objects.filter(author=request.user)
    return render(request, 'blog/post_list.html', {'posts': posts})


def bookmarks(request):
    posts = Post.objects.filter(published_date__lte=timezone.now(), author=request.user).order_by('published_date')
    return render(request, 'blog/bookmarks.html', {'posts': posts})


def post_favorite(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.is_favorite:
        post.is_favorite = False
    else:
        post.is_favorite = True
    post.save()
    return redirect('blog:blog.views.post_list')


@login_required
def post_new(request):
    if not request.user.is_authenticated():
        return render(request, 'blog/login.html')
    if request.method == "POST":
        form = PostForm(request.POST or None, request.FILES or None)  # PostForm-name of form in forms.py #request.FILES for uploading image
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.image = request.FILES['image']
            """
            file_type = post.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'post': post,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'blog/post_edit.html', context)
            """
            # if post.image!=None:
                # post.save()

            #  post.published_date = timezone.now()
            form.save()
            messages.success(request, "New post successfully created!")
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:blog.views.post_list')
    if request.method == "POST":
        form = PostForm(request.POST or None, request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save() #save the corresponding changes in database
            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


@login_required()
def edit_profile(request):
    if not request.user.is_authenticated():
        return render(request, 'blog/login.html')
    if request.method == "POST":
        form = UserProfile(request.POST or None, request.FILES or None)#PostForm-name of form in forms.py #request.FILES for uploading image
        if form.is_valid():
            profile = form.save(commit=False)
            form.save()
            return redirect('blog.views.post_list')
    else:
        profile = UserProfile()
    return render(request, 'blog/user_profile.html', {'profile': profile})


@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True, author=request.user).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})


@login_required
def confirm_post_delete(request, pk):
    object = get_object_or_404(Post, pk=pk)
    if object.author != request.user:
        return redirect('blog:blog.views.post_list')
    if request.method == "POST":
        object.delete()
        return redirect('blog:blog.views.post_list')
    context = {'object': object}
    context = {'object': object}
    return render(request, 'blog/confirm_post_delete.html', context)


@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    #messages.success(request, "Post successfully published!")
    return redirect('blog:blog.views.post_detail', pk=post.pk) 	#return redirect('blog.views.post_detail', pk=pk)

"""
@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog:blog.views.post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('blog:blog.views.post_detail', pk=post_pk)
"""
