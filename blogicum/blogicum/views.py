from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
import os

from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView
from django.core.mail import send_mail
from django.conf import settings

from django.core.wsgi import get_wsgi_application

#from blogicum.blog.models import Post, User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')

application = get_wsgi_application()


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class RulesPageView(TemplateView):
    template_name = "pages/rules.html"

def send_notification_email(to_email):
    send_mail(
        subject='Добро пожаловать на сайт!',
        message='Спасибо за регистрацию на нашем сайте.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        fail_silently=False,
    )


# class RegisterView(CreateView):
#     form_class = UserCreationForm
#     template_name = 'registration/registration_form.html'
#     success_url = reverse_lazy('login')





class LoginView:
    @classmethod
    def as_view(cls):
        pass