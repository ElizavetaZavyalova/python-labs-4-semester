from . import views
from django.urls import path, include


urlpatterns = [
    path('', views.index, name='home'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('about-us', views.about, name='about'),
    path('create', views.create, name='create'),
    path('author', views.author, name='author'),

    path('<int:pk>/', views.DetailDetailView.as_view(), name='detail'),
    path('<int:pk>/update', views.TaskUpdateView.as_view(), name='update'),
    path('<int:pk>/delete', views.TaskDeleteView.as_view(), name='delete'),
]
