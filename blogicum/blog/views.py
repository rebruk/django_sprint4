from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import (
    FormView, CreateView, ListView, DeleteView,
    DetailView, UpdateView, RedirectView
)
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from .forms import PostForm, CommentForm
from .models import Comment, Post, Category
from .mixins import OnlyAuthorMixin


class RegistrationView(FormView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class IndexView(ListView):
    """Главная страница сайта."""

    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'object_list'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        return (
            Post.objects
            .published()
            .with_comments_count()
            .ordered()
        )


class CategoryView(LoginRequiredMixin, ListView):
    """Страница публикаций конкретной категории."""

    template_name = 'blog/category.html'
    context_object_name = 'object_list'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True
        )
        return self.category.posts.published().ordered().with_comments_count()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    model = Post
    template_name = "blog/profile.html"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        user_profile = get_object_or_404(
            User,
            username=self.kwargs["username"]
        )
        self.profile = user_profile

        queryset = self.profile.posts.with_related().with_comments_count()

        if not self.request.user.is_authenticated or \
                self.request.user != user_profile:
            queryset = queryset.published()

        return queryset.ordered()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        context["author_post"] = self.request.user == self.profile
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = "blog/user.html"
    fields = ["first_name", "last_name", "username", "email"]

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={"username": self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        if not post.category:
            post.category = None
        post.save()
        return redirect('blog:profile', username=self.request.user.username)


class PostDetailView(LoginRequiredMixin, DetailView):
    """Детали публикации."""

    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_object(self, **kwargs):
        queryset = self.model.objects.filter(pk=self.kwargs['post_id'])

        post = queryset.first()
        if post is None:
            raise Http404

        if self.request.user == post.author:
            return get_object_or_404(queryset)

        queryset = queryset.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

        return get_object_or_404(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.order_by("created_at")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = request.user
        comment.save()
        return redirect("blog:post_detail", post_id=self.object.id)


class PostEditView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        self.object = self.get_object()
        return (
            self.request.user.is_authenticated
            and self.object.author == self.request.user
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return redirect(reverse(
                'blog:post_detail', kwargs={"post_id": self.object.pk}
            ))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={"post_id": self.object.pk})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Удаление публикации."""

    model = Post
    template_name = "blog/create.html"

    def get_success_url(self):
        return reverse("blog:index")


class AddCommentView(LoginRequiredMixin, FormView):
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(
            Post,
            id=self.kwargs['post_id'],
            is_published=True
        )

        form.instance.post = post
        form.instance.author = self.request.user
        form.save()
        return redirect('blog:post_detail', post_id=post.id)


class EditCommentView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.id})


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"]
        )

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.kwargs["post_id"]}
        )


class ChangePasswordView(LoginRequiredMixin, RedirectView):
    pattern_name = 'password_change'
