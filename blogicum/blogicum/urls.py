from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
#from .views import RegisterView#, ProfileView, AboutPageView,
from . import views
from django.views.generic.edit import CreateView
from django.urls import include, path, reverse_lazy
from django.contrib.auth.forms import UserCreationForm

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.error_500'
handler403 = 'pages.views.csrf_failure'

urlpatterns = [
    path('', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    ]# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)