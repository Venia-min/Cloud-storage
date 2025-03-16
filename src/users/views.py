from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

from src.users.forms import UserRegistrationForm, UserLoginForm


def index_view(request):
    return render(request, "index.html")


def search_view(request):
    return render(request, "search.html")


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")

    else:
        form = UserLoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
