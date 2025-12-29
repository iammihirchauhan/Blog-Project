from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .models import Blog, Comment
import json
from .util import auth_required


@auth_required
def home(request):
    return redirect("blog_list")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "success": False,
                    "field": "username",
                    "error": "Username already exists",
                }
            )

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "field": "email", "error": "Email already exists"}
            )

        User.objects.create_user(username=username, email=email, password=password)

        return JsonResponse({"success": True})

    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    "success": False,
                    "field": "username",
                    "error": "Username does not exist",
                }
            )

        user = authenticate(request, username=username, password=password)

        if not user:
            return JsonResponse(
                {"success": False, "field": "password", "error": "Incorrect password"}
            )

        login(request, user)
        return JsonResponse({"success": True})

    return render(request, "auth/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@method_decorator(auth_required, name="dispatch")
class BlogsView(View):
    @auth_required
    def get(self, request):
        blogs = Blog.objects.all().order_by("-created_at")
        return render(request, "blogs/blog_list.html", {"blogs": blogs})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        title = (data.get("title") or "").strip()
        content = (data.get("content") or "").strip()

        if not title or not content:
            return JsonResponse({"error": "Title and content required"}, status=400)

        Blog.objects.create(user=request.user, title=title, content=content)

        return JsonResponse({"success": True})


@method_decorator(auth_required, name="dispatch")
class BlogDetailView(View):
    def get(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk, user=request.user)
        return JsonResponse(
            {
                "id": blog.id,
                "title": blog.title,
                "content": blog.content,
            }
        )

    def put(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk, user=request.user)

        data = json.loads(request.body or "{}")
        title = (data.get("title") or "").strip()
        content = (data.get("content") or "").strip()

        if not title or not content:
            return JsonResponse({"error": "Title and content required"}, status=400)

        blog.title = title
        blog.content = content
        blog.save()
        return JsonResponse({"success": True})

    def delete(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk, user=request.user)
        blog.delete()
        return JsonResponse({"success": True})


@auth_required
def blog_page(request, blog_id):
    blog = get_object_or_404(Blog.objects.select_related("user"), id=blog_id)

    comments = (
        Comment.objects.filter(blog=blog).select_related("user").order_by("created_at")
    )

    if request.method == "POST":
        data = json.loads(request.body)
        text = (data.get("comment") or "").strip()

        if not text:
            return JsonResponse({"success": False})

        comment = Comment.objects.create(blog=blog, user=request.user, text=text)

        return JsonResponse(
            {
                "success": True,
                "id": comment.id,
                "username": comment.user.username,
                "text": comment.text,
                "time": "just now",
                "is_owner": True,
            }
        )

    return render(
        request,
        "detail/blog_detail.html",
        {"blog": blog, "comments": comments},
    )


@auth_required
def comment_detail(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == "PUT":
        data = json.loads(request.body)
        text = (data.get("text") or "").strip()

        if not text:
            return JsonResponse({"success": False})

        comment.text = text
        comment.save()
        return JsonResponse({"success": True})

    if request.method == "DELETE":
        comment.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Method not allowed"}, status=405)
