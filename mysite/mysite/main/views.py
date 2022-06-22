from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Article, User
from .forms import ArticleForm
from django.http import Http404, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib import auth
from django.views.generic import UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy

# Create your views here.

from django.core.exceptions import ObjectDoesNotExist


def index(request):
    tasks = Article.objects.all()
    return render(request, 'main/index.html', {'title': 'Главная страница сайта', 'tasks': tasks})


class TaskDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('home')
    template_name = 'main/delete.html'


class DetailDetailView(DetailView):
    model = Article
    template_name = 'main/detail.html'
    context_object_name = 'article'


class TaskUpdateView(UpdateView):
    model = Article
    template_name = 'main/update.html'
    form_class = ArticleForm


def about(request):
    return render(request, 'main/about.html')


def author(request):
    return render(request, 'main/author.html')


def create(request):
    error = ""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            error = "Форма не верная!!!"
    form = ArticleForm()
    data = {
        'form': form,
        'error': error
    }

    return render(request, 'main/create.html', data)
