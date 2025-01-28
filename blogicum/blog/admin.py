from django.contrib import admin
from .models import Post, Category, Location, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "pub_date")
    search_fields = ("title", "text")
    list_filter = ("is_published", "category", "pub_date")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published")
    list_filter = ("is_published",)
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published")
    search_fields = ("title",)
    list_filter = ("is_published",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text", "created_at")
    search_fields = ("text", "author__username", "post__title")
    list_filter = ("created_at", "post", "author")
