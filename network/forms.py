from django.forms import ModelForm
from django import forms
from .models import Post, Comment

# create a new post form model from class
class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["headline", "content"]
        widgets = {
            "headline": forms.TextInput(
                attrs={
                    "placeholder": "What's happening?",
                    "class": "form-control",
                    "id": "compose-post-headline"
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "placeholder": "What are you thinking about?",
                    "class": "form-control",
                    "id": "compose-post-content",
                    "rows": 3
                }
            )
        }