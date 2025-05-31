# drone/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DroneInspection
from plant.models import SolarPlant, Zone
from .forms import DroneInspectionForm # คุณต้องมี forms.py และ DroneInspectionForm ที่ถูกต้อง
from django.conf import settings # ถ้าคุณใช้ settings เช่น settings.AUTH_USER_MODEL โดยตรง
from datetime import date
from django.utils.timezone import make_aware
from django.db import models

# from django.utils import timezone # ไม่จำเป็นใน view นี้ถ้า model ไม่ได้ใช้ timezone ใน save() พิเศษ



# =============================
# DRONE CONTROLLER: Upload View
# =============================
@login_required
def upload_inspection(request):
    if not hasattr(request.user, 'role') or request.user.role != 'drone_controller':
        return redirect('no_permission')

    zone_id = request.GET.get('zone_id')
    zone = Zone.objects.get(id=zone_id)

    if request.method == 'POST':
        form = DroneInspectionForm(request.POST or None, request.FILES or None, user=request.user)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.captured_by = request.user
            inspection.captured_date = date.today()
            inspection.zone = zone
            inspection.save()
        return redirect('drone_status')
    else:
        form = DroneInspectionForm(request.POST or None, request.FILES or None, user=request.user)

    return render(request, 'dashboard/upload_inspection.html', {
        'form': form,
        'zone': zone,
    })

@login_required
def drone_status_view(request):
    if not hasattr(request.user, 'role') or request.user.role != 'drone_controller':
        return redirect('no_permission')

    today = date.today()

    inspections = DroneInspection.objects.filter(
        captured_by=request.user
    ).filter(
        models.Q(status='pending') |
        models.Q(status='issue_found') |
        (models.Q(status='analyzed') & models.Q(captured_date=today))
    ).select_related('analyzed_by').order_by('-captured_date', '-captured_time')


    return render(request, 'dashboard/status.html', {
        'inspections': inspections,
    })


@login_required
def edit_inspection(request, inspection_id):
    inspection = get_object_or_404(DroneInspection, pk=inspection_id)

    # Permission check
    can_edit = False
    if request.user == inspection.captured_by:
        can_edit = True
    elif hasattr(request.user, 'role') and request.user.role == 'admin':
        can_edit = True

    if not can_edit:
        messages.error(request, "You do not have permission to edit this inspection.")
        return redirect('drone_status')

    if request.method == 'POST':
        form = DroneInspectionForm(request.POST or None, request.FILES or None, user=request.user, instance=inspection)
        if form.is_valid():
            try:
                updated_inspection = form.save(commit=False)
                updated_inspection.status = 'pending'  # ✅ เปลี่ยนสถานะกลับเป็น pending
                updated_inspection.save()

                messages.success(request, "Inspection details updated successfully and set to pending.")
                return redirect('drone_status')
            except Exception as e:
                messages.error(request, f"An error occurred while saving the inspection: {str(e)}")
        else:
            messages.error(request, "Please correct the errors shown below.")
    else:
        form = DroneInspectionForm(user=request.user)

    return render(request, 'dashboard/edit_inspection.html', {
        'form': form,
        'inspection': inspection
    })


@login_required
def plant_detail_view(request, plant_id):
    # ดึงเฉพาะโรงไฟฟ้าที่ drone_controller เป็น user นี้เท่านั้น
    plant = get_object_or_404(SolarPlant, id=plant_id, drone_controller=request.user)

    zones = plant.zones.prefetch_related('rows__panels')  # ดึงข้อมูลเชิงลึกแบบ efficient
    return render(request, 'dashboard/plant_detail.html', {
        'plant': plant,
        'zones': zones,
    })

def ajax_get_zones_by_plant(request, plant_id):
    zones = Zone.objects.filter(plant_id=plant_id).values('id', 'name')
    return JsonResponse(list(zones), safe=False)


@login_required
def drone_task_view(request):
    today = date.today()
    plants = SolarPlant.objects.filter(drone_controller=request.user).prefetch_related('zones')
    tasks = []

    for plant in plants:
        for zone in plant.zones.all():
            # ตรวจว่ามี inspection ที่อัปโหลดวันนี้แล้วหรือยัง
            uploaded = DroneInspection.objects.filter(
                plant=plant,
                zone=zone,
                captured_date=today,
                captured_by=request.user
            ).exists()

            tasks.append({
                'plant': plant,
                'zone': zone,
                'uploaded': uploaded,
            })

    return render(request, 'dashboard/drone_tasks.html', {
        'today': today,
        'tasks': tasks,
    })


@login_required
def data_analyst_dashboard(request):
    if not hasattr(request.user, 'role') or request.user.role != 'data_analyst':
        return redirect('no_permission')
    
    # Fetch drone inspection data that needs analysis
    drone_controller_data = DroneInspection.objects.all().order_by('-captured_at')
    
    # Group inspections by status
    pending_inspections = drone_controller_data.filter(status='pending').count()
    analyzed_inspections = drone_controller_data.filter(status='analyzed').count()
    issue_found_inspections = drone_controller_data.filter(status='issue_found').count()
    completed_inspections = drone_controller_data.filter(status='complete').count()
    
    context = {
        'drone_controller_data': drone_controller_data,
        'stats': {
            'pending': pending_inspections,
            'analyzed': analyzed_inspections,
            'issues': issue_found_inspections,
            'completed': completed_inspections
        }
    }
    return render(request, 'dashboard/data_analyst_dashboard.html', context)