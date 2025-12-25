from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("blogs/", views.BlogsView.as_view(), name="blog_list"),
    path("blogs/<int:blog_id>/", views.BlogDetailView.as_view(), name="blog_detail"),  
]
