from django.db import models
from django.utils import timezone
from django.db.models import Count


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    def with_comments_count(self):
        return self.annotate(comment_count=Count('comments'))
