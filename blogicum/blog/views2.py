from django.shortcuts import redirect, get_object_or_404
from django.utils.timezone import now
from django.views.generic import FormView, CreateView, ListView, DeleteView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Count
from django.conf import settings
from .forms import PostForm, CommentForm
from .models import Post, Comment, Category
from pages.views import csrf_failure


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки, что текущий пользователь — автор объекта."""
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return csrf_failure(self.request, reason="Вы не являетесь автором этого объекта.")


class IndexView(ListView):
    """Главная страница с опубликованными публикациями."""
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        return Post.objects.filter(is_published=True, pub_date__lte=now()) \
            .annotate(comment_count=Count('comments')).order_by('-pub_date')


class CategoryView(LoginRequiredMixin, ListView):
    """Страница публикаций конкретной категории."""
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_published=True)
        return Post.objects.filter(category=self.category, is_published=True) \
            .annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(LoginRequiredMixin, ListView):
    """Страница профиля с публикациями пользователя."""
    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        user_profile = get_object_or_404(User, username=self.kwargs["username"])
        queryset = Post.objects.filter(author=user_profile).annotate(comment_count=Count("comments")) \
            .order_by("-pub_date")
        if self.request.user != user_profile:
            queryset = queryset.filter(pub_date__lte=now(), is_published=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(User, username=self.kwargs["username"])
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostEditView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """Редактирование публикации."""
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Удаление публикации."""
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")


class AddCommentView(LoginRequiredMixin, FormView):
    """Добавление комментария к публикации."""
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'], is_published=True)
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
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.post.id})


class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""
    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})
