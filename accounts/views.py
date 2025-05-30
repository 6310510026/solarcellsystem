from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import CustomUser

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

        messages.success(request, "Registration successful. Await admin approval.")
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
    from plant.models import SolarPlant, Zone
    from drone.models import DroneInspection
    plants = SolarPlant.objects.all().prefetch_related('zones', 'owner')
    plant_name = request.GET.get('plant_name', '').strip()
    zone_name = request.GET.get('zone_name', '').strip()
    owner_name = request.GET.get('owner_name', '').strip()

    if plant_name:
        plants = plants.filter(name__icontains=plant_name)
    if owner_name:
        plants = plants.filter(owner__username__icontains=owner_name)
    if zone_name:
        plants = plants.filter(zones__name__icontains=zone_name).distinct()

    # Overview card context
    total_plants = SolarPlant.objects.count()
    analyzed_plant_ids = DroneInspection.objects.exclude(status='pending').values_list('plant_id', flat=True).distinct()
    analyzed_plants = SolarPlant.objects.filter(id__in=analyzed_plant_ids).count()

    return render(request, 'dashboard/data_analyst_dashboard.html', {
        'plants': plants,
        'total_plants': total_plants,
        'analyzed_plants': analyzed_plants,
    })

@login_required
def drone_controller_dashboard_view(request):
    user = request.user
    plants = user.assigned_drone_plants.all()
    return render(request, 'dashboard/drone_controller_dashboard.html', {'plants': plants})

@login_required
def site_admin_dashboard_view(request):
    return render(request, 'dashboard/site_admin_dashboard.html')

@login_required
def plant_detail_analyst_view(request, plant_id):
    from plant.models import SolarPlant
    plant = get_object_or_404(SolarPlant, id=plant_id)
    zones = plant.zones.prefetch_related('droneinspection_set')
    return render(request, 'dashboard/plant_detail_analyst.html', {
        'plant': plant,
        'zones': zones,
    })



@login_required
def complete_profile(request):
    user = request.user

    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['plant_owner', 'data_analyst', 'drone_controller']:
            user.role = role
            user.is_active = False  # deactivate จนกว่า admin จะอนุมัติ
            user.save()
            messages.success(request, "Registration successful. Await admin approval.")
            return redirect('login_page')  # แจ้งให้รอ approval
    return render(request, 'select_role.html')

@login_required
def complete_profile(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
        else:
            user = request.user
            user.role = role
            user.set_password(password1)
            user.is_active = False  # ต้องให้ admin อนุมัติ
            user.save()
            messages.success(request, "Profile updated. Waiting for admin approval.")
            return redirect('login_page')

    return render(request, 'select_role.html')
