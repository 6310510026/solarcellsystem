from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

# ---------- REGISTER ----------
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register_page')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register_page')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role
        )
        user.is_active = False  # 🔴 ปิดการใช้งานจนกว่า admin จะอนุมัติ
        user.save()

        messages.success(request, "ลงทะเบียนสำเร็จ! โปรดรอผู้ดูแลระบบอนุมัติบัญชีก่อนเข้าใช้งาน")
        return redirect('login_page')
    return render(request, 'register.html')

# ---------- LOGIN ----------
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.warning(request, "บัญชีของคุณยังไม่ได้รับการอนุมัติจากผู้ดูแลระบบ")
                return redirect('login_page')
        except User.DoesNotExist:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            return redirect('login_page')

        # ตรวจ password แบบ manual
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('role_redirect')
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
            return redirect('login_page')

    return render(request, 'login.html')

# ---------- LOGOUT ----------
def logout_user(request):
    logout(request)
    return redirect('login_page')

# ---------- REDIRECT BY ROLE ----------
@login_required
def role_redirect(request):
    user = request.user
    if user.role == 'plant_owner':
        return redirect('plant_owner_dashboard')
    elif user.role == 'data_analyst':
        return redirect('data_analyst_dashboard')
    elif user.role == 'drone_controller':
        return redirect('drone_controller_dashboard')
    elif user.role == 'site_admin':
        return redirect('/admin/')
    return redirect('/')


@login_required
def plant_owner_dashboard_view(request):
    return render(request, 'dashboard/plant_owner_dashboard.html')

@login_required
def data_analyst_dashboard_view(request):
    return render(request, 'dashboard/data_analyst_dashboard.html')

@login_required
def drone_controller_dashboard_view(request):
    user = request.user
    plants = user.assigned_drone_plants.all()
    return render(request, 'dashboard/drone_controller_dashboard.html', {'plants': plants})

@login_required
def site_admin_dashboard_view(request):
    return render(request, 'dashboard/site_admin_dashboard.html')
