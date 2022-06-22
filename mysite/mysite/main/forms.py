from .models import Article
from django.forms import ModelForm, TextInput, Textarea
from django import forms


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ["title", "text"]
        widgets = {"title": TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Введите название'}),
                   "text": Textarea(attrs={'class': 'form-control',
                                           'placeholder': 'Введите описание'}),
                   }


class TaskFormRefactor(ModelForm):
    class Meta:
        model = Article()
        fields = ["title", "text"]
        widgets = {"title": TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Введите название'}),
                   "text": Textarea(attrs={'class': 'form-control',
                                           'placeholder': 'Введите описание'}),
                   }
