import os

from django.views.generic import TemplateView
from django.core.mail import send_mail
from django.conf import settings

from django.core.wsgi import get_wsgi_application

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


class LoginView:
    @classmethod
    def as_view(cls):
        pass