from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('api/blog/<slug:slug>/view/', views.increment_view_count, name='blog_increment_view'),
]

