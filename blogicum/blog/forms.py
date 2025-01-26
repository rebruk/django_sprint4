from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'location', 'pub_date', 'is_published', 'image', 'text']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 40})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']