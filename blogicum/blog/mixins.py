from pages.views import csrf_failure
from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return csrf_failure(
            self.request,
            reason="Вы не являетесь автором этого объекта."
        )
