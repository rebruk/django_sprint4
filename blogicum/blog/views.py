from django.utils.timezone import now
from django.shortcuts import render, get_object_or_404, redirect

from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, UserChangeForm
from django.contrib.auth import update_session_auth_hash

from django.views.generic import FormView, CreateView, ListView, DeleteView, DetailView, UpdateView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from .forms import PostForm, CommentForm
from .models import Comment, Post, Category
from django.db.models import Count
from pages.views import csrf_failure

class OnlyAuthorMixin(UserPassesTestMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        return super().dispatch(request, *args, **kwargs)
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        return csrf_failure(self.request, reason="Вы не являетесь автором этого объекта.")


class RegistrationView(FormView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class IndexView(ListView):
    """
    Главная страница сайта с отображением уже опубликованных публикаций
    """
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        return (
            Post.objects.filter(
                is_published=True,
                pub_date__lte=now()
            )
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )


class CategoryView(LoginRequiredMixin, ListView):
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'], is_published=True)
        return Post.objects.filter(
            is_published=True
        ).annotate(comment_count=Count('comments')
                   ).order_by('-pub_date')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(LoginRequiredMixin, ListView):
    """
    Страница профиля пользователя с отображением всех его публикаций.
    """
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        user_profile = get_object_or_404(User, username=self.kwargs["username"])
        queryset = (
            Post.objects.filter(author=user_profile)
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

        if self.request.user != user_profile:
            queryset = queryset.filter(pub_date__lte=now(), is_published=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = get_object_or_404(User, username=self.kwargs["username"])
        return context


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username'],
            is_published=True
        )

    def get_context_data(self, **kwargs):
        print("Метод get_context_data вызван")
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['posts'] = Post.objects.filter(author=user)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """
    Страница редактирования профиля. Пользователь может изменять
    только имя, фамилию, логин и адрес электронной почты.
    """
    template_name = "blog/user.html"
    fields = ["first_name", "last_name", "username", "email"]

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("profile", kwargs={"username": self.request.user.username})

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Страница создания новой публикации.
    """
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

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(LoginRequiredMixin, DetailView):
    """
    Страница детальной информации о публикации.
    """
    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_object(self):
        post = Post.objects.filter(pk=self.kwargs['post_id']).first()
        if not post:
            return page_not_found(self.request, None)
        return post


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.order_by("created_at")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect("blog:post_detail", post_id=self.object.id)
        return self.render_to_response(self.get_context_data(form=form))


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование публикации.
    """
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def get_object(self):
        return get_object_or_404(Post, id=self.kwargs["post_id"], is_published=True)

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """
    Удаление публикации.
    """
    model = Post
    template_name = "blog/create.html"
    success_url = reverse_lazy("blog:index")


class AddCommentView(LoginRequiredMixin, FormView):
    model = Comment
    form_class = CommentForm
    template_name = None

    def form_valid(self, form):
        post = get_object_or_404(Post, id=self.kwargs['post_id'], is_published=True)
        comment = form.save(commit=False)
        comment.post = post
        comment.author = self.request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post.id)

    def form_invalid(self, form):
        """
        Если форма не прошла валидацию, перенаправляем на ту же страницу поста.
        """
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get(self, request, *args, **kwargs):
        """
        Перенаправляем на страницу поста, если запрос GET.
        """
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class EditCommentView(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    """
    Редактирование комментария.
    """
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'


    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.object.post.id})



class CommentDeleteView(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    """
    Удаление комментария.
    """
    model = Comment
    pk_url_kwarg = "comment_id"
    context_object_name = "comment"
    template_name = "blog/comment.html"
    success_url = reverse_lazy("blog:index")

    def get_object(self):
        return get_object_or_404(
            Comment, id=self.kwargs["comment_id"], post_id=self.kwargs["post_id"]
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]})

class ChangePasswordView(LoginRequiredMixin, RedirectView):
    pattern_name = 'password_change'
