from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category_posts'),

    path('login', views.ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),

    path('auth/registration/', views.RegistrationView.as_view(), name='registration'),
    path('auth/', include('django.contrib.auth.urls')),

    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path("posts/<int:post_id>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:post_id>/edit/", views.PostEditView.as_view(), name="edit_post"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete_post"),
    path('posts/<int:post_id>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/', views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name="delete_comment",
    ),
    path('profile/password/', views.ChangePasswordView, name='password_change'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
