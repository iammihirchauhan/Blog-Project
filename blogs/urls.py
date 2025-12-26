from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("blogs/", views.BlogsView.as_view(), name="blog_list"),
    path("blogs/<int:pk>/", views.BlogDetailView.as_view(), name="blog_detail"),
    path("blogs/all/", views.blog_page, name="blog_page"),
]
