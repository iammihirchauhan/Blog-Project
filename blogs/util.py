from functools import wraps
from django.shortcuts import redirect


def auth_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request = getattr(args[0], "request", args[0]) if args else None

        if request and not request.user.is_authenticated:
            return redirect("login")

        return view_func(*args, **kwargs)

    return wrapper
