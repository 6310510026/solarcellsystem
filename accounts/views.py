from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


def register_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register_page")

        try:
            validate_password(password1)  # ตรวจสอบความแข็งแกร่งของรหัสผ่าน
        except ValidationError as e:
            messages.error(request, e.messages[0])  # แสดงข้อความแจ้งข้อผิดพลาด
            return redirect("register_page")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register_page")
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register_page")

        user = CustomUser.objects.create_user(username=username, email=email, password=password1, role=role)
        user.save()
        messages.success(request, "Account created successfully.")
        return redirect("login_page")
    return render(request, "register.html")

def login_page(request):
    if request.user.is_authenticated:
        return redirect("index")  # หากล็อกอินแล้ว ให้ไปหน้า index
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def logout_page(request):
    logout(request)
    return redirect("login_page")

@login_required
def plant_owner_dashboard(request):
    return render(request, "plant_owner_dashboard.html",)

@login_required
def data_analyst_dashboard(request):
    return render(request, "data_analyst_dashboard.html",)

@login_required
def drone_controller_dashboard(request):
    return render(request, "drone_controller_dashboard.html",)

@login_required
def index(request):
    if request.user.is_authenticated:
        if request.user.is_plant_owner():
            return redirect("plant_owner_dashboard")
        #elif request.user.is_site_admin():
        #    return redirect("site_admin_dashboard") #ตรงนี้ต้องแก้
        elif request.user.is_data_analyst():
            return redirect("data_analyst_dashboard")
        elif request.user.is_drone_controller():
            return redirect("drone_controller_dashboard")       
    return redirect("login_page")  # หากไม่ผ่านเงื่อนไขใดเลย ให้ไปหน้า login

@login_required
def success(request):
    return render(request, "success_login.html",)