from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from plant.models import SolarPlant, Zone, SolarPanel, PanelOutputLog
from drone.models import DroneInspection
from django.db.models import Count
from django.db import models
import json
from datetime import datetime, timedelta

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
    plant = get_object_or_404(SolarPlant, id=plant_id)
    zones = plant.zones.prefetch_related('droneinspection_set')
    return render(request, 'dashboard/plant_detail_analyst.html', {
        'plant': plant,
        'zones': zones,
    })

@login_required
def data_analyst_analytics_view(request):
    # Filter เฉพาะโรงไฟฟ้าที่ data_analyst เป็น user ปัจจุบัน
    plants = SolarPlant.objects.filter(data_analyst=request.user).select_related('owner', 'data_analyst').prefetch_related('zones')
    plant_data = []
    for plant in plants:
        panels = SolarPanel.objects.filter(row__zone__plant=plant)
        num_panels = panels.count()
        if num_panels == 0 or not plant.installed_capacity_kw:
            efficiency = None
        else:
            installed_per_panel = float(plant.installed_capacity_kw) / num_panels
            actual_sum = sum(float(p.actual_output_kw or 0) for p in panels)
            installed_sum = installed_per_panel * num_panels
            efficiency = (actual_sum / installed_sum * 100) if installed_sum else 0
        zones = plant.zones.all()
        plant_data.append({
            'id': plant.id,
            'name': plant.name,
            'location': plant.location,
            'owner': plant.owner.username,
            'efficiency': efficiency,
            'zones': zones,
        })
    context = {
        'plant_data': plant_data,
    }
    return render(request, 'dashboard/analytics.html', context)

@login_required
def panel_analytics_view(request, plant_id):
    plant = get_object_or_404(SolarPlant, id=plant_id)
    panels = SolarPanel.objects.filter(row__zone__plant=plant).select_related('row')
    num_panels = panels.count()
    installed_per_panel = float(plant.installed_capacity_kw) / num_panels if num_panels and plant.installed_capacity_kw else 0
    panel_data = []
    panel_choices = []

    # --- Handle POST for updating actual_output_kw ---
    if request.method == 'POST':
        for panel in panels:
            field_name = f'actual_output_{panel.id}'
            if field_name in request.POST:
                try:
                    value = float(request.POST.get(field_name, '0'))
                    panel.actual_output_kw = value
                    panel.save()
                except ValueError:
                    pass  # ignore invalid input
        return redirect('panel_analytics', plant_id=plant.id)

    for panel in panels:
        actual = float(panel.actual_output_kw) if panel.actual_output_kw is not None else 0
        efficiency = (actual / installed_per_panel * 100) if installed_per_panel else 0
        panel_data.append({
            'panel': f"R{panel.row.row_number}-C{panel.column_number}",
            'panel_id': panel.id,
            'actual_output_kw': actual,
            'efficiency': efficiency,
        })
        panel_choices.append({'id': panel.id, 'name': f"R{panel.row.row_number}-C{panel.column_number}"})

    # --- Efficiency by time (all panels) ---
    logs = PanelOutputLog.objects.filter(panel__row__zone__plant=plant)
    if logs.exists():
        time_eff = {}
        for log in logs.order_by('timestamp'):
            t = log.timestamp.strftime('%Y-%m-%d %H:%M')
            if t not in time_eff:
                time_eff[t] = {'actual_sum': 0, 'count': 0}
            time_eff[t]['actual_sum'] += float(log.output_kw)
            time_eff[t]['count'] += 1
        efficiency_by_time = []
        for t, v in time_eff.items():
            installed_sum = installed_per_panel * v['count']
            eff = (v['actual_sum'] / installed_sum * 100) if installed_sum else 0
            efficiency_by_time.append({'timestamp': t, 'efficiency': eff})
        # Per panel
        panel_eff_by_time = {}
        for panel in panels:
            logs = panel.output_logs.order_by('timestamp')
            panel_eff_by_time[panel.id] = [
                {
                    'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'efficiency': (float(log.output_kw) / installed_per_panel * 100) if installed_per_panel else 0
                }
                for log in logs
            ]
    else:
        # MOCK: สร้างข้อมูล 7 วันย้อนหลัง (ทุกวัน)
        now = datetime.now()
        efficiency_by_time = []
        panel_eff_by_time = {}
        for i in range(7, 0, -1):
            ts = (now - timedelta(days=i)).strftime('%Y-%m-%d %H:%M')
            eff = sum(p['efficiency'] for p in panel_data) / len(panel_data) if panel_data else 0
            efficiency_by_time.append({'timestamp': ts, 'efficiency': eff})
        for idx, panel in enumerate(panels):
            panel_eff_by_time[panel.id] = [
                {
                    'timestamp': (now - timedelta(days=i)).strftime('%Y-%m-%d %H:%M'),
                    'efficiency': float(panel_data[idx]['efficiency']) if len(panel_data) > idx else 0
                }
                for i in range(7, 0, -1)
            ]

    # Pie chart data for panel status
    normal_count = sum(1 for p in panel_data if p['efficiency'] >= 80)
    medium_count = sum(1 for p in panel_data if 50 <= p['efficiency'] < 80)
    abnormal_count = sum(1 for p in panel_data if p['efficiency'] < 50)

    context = {
        'plant': plant,
        'panel_data': panel_data,
        'installed_per_panel': installed_per_panel,
        'efficiency_by_time': json.dumps(efficiency_by_time),
        'panel_eff_by_time': json.dumps(panel_eff_by_time),
        'panel_choices': panel_choices,
        'normal_count': normal_count,
        'medium_count': medium_count,
        'abnormal_count': abnormal_count,
    }
    return render(request, 'dashboard/panel_analytics.html', context)

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
