from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        small_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2}),
        }
