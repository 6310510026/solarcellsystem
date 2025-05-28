# drone/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DroneInspection
from plant.models import SolarPlant
from .forms import DroneInspectionForm # คุณต้องมี forms.py และ DroneInspectionForm ที่ถูกต้อง
from django.conf import settings # ถ้าคุณใช้ settings เช่น settings.AUTH_USER_MODEL โดยตรง
# from django.utils import timezone # ไม่จำเป็นใน view นี้ถ้า model ไม่ได้ใช้ timezone ใน save() พิเศษ



# =============================
# DRONE CONTROLLER: Upload View
# =============================
@login_required
def upload_inspection(request):
    # ตรวจสอบว่า User model ของคุณมี attribute 'role' จริงหรือไม่
    if not hasattr(request.user, 'role') or request.user.role != 'drone_controller':
        # messages.error(request, "You do not have permission to upload.") # Optional message
        return redirect('no_permission') # ตรวจสอบว่ามี URL name 'no_permission'

    if request.method == 'POST':
        form = DroneInspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.captured_by = request.user
            inspection.save() # นี่จะเรียก model's save()
            messages.success(request, "อัปโหลดภาพเรียบร้อยแล้ว")
            return redirect('drone_status') # ตรวจสอบว่ามี URL name 'drone_status'
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DroneInspectionForm()

    return render(request, 'dashboard/upload_inspection.html', {'form': form})

@login_required
def drone_status_view(request):
    if not hasattr(request.user, 'role') or request.user.role != 'drone_controller':
        # messages.error(request, "You do not have permission to view this page.") # Optional message
        return redirect('no_permission')

    # การเรียงลำดับใน status view:
    # ถ้าต้องการเรียงตามเวลาที่ผู้ใช้ป้อน จะซับซ้อนกว่าเพราะเป็นสองฟิลด์
    # ปัจจุบันเรียงตาม captured_at (เวลาที่ระบบบันทึก) ซึ่งก็สมเหตุสมผลสำหรับการดูรายการล่าสุด
    inspections = DroneInspection.objects.filter(captured_by=request.user).order_by('-captured_at')
    return render(request, 'dashboard/status.html', {'inspections': inspections})

@login_required # เพิ่ม @login_required ถ้ายังไม่มี
def edit_inspection(request, inspection_id):
    inspection = get_object_or_404(DroneInspection, pk=inspection_id)

    # Permission check (ตัวอย่าง - ปรับตาม logic ของคุณ)
    can_edit = False
    if request.user == inspection.captured_by:
        can_edit = True
    # ตรวจสอบว่า User model ของคุณมี attribute 'role' จริงหรือไม่
    elif hasattr(request.user, 'role') and request.user.role == 'admin':
        can_edit = True
    
    if not can_edit:
        messages.error(request, "You do not have permission to edit this inspection.")
        return redirect('drone_status')

    if request.method == 'POST':
        print("Request POST data:", request.POST) # DEBUG: ดูข้อมูลที่ส่งมาจากฟอร์ม
        form = DroneInspectionForm(request.POST, request.FILES, instance=inspection)
        if form.is_valid():
            print("Form is valid. Attempting to save...") # DEBUG
            try:
                updated_inspection = form.save() # เรียก form.save() ซึ่งจะเรียก model.save()

                # Debugging prints ที่ตรงกับฟิลด์ปัจจุบัน
                print(f"Cleaned data date: {form.cleaned_data.get('captured_date')}") # DEBUG
                print(f"Cleaned data time: {form.cleaned_data.get('captured_time')}") # DEBUG
                print(f"Inspection (ID: {updated_inspection.pk}) saved.") # DEBUG
                # แสดงค่า captured_date และ captured_time ที่บันทึกแล้ว
                print(f"Saved captured_date: {updated_inspection.captured_date}") # DEBUG
                print(f"Saved captured_time: {updated_inspection.captured_time}") # DEBUG

                messages.success(request, "Inspection details updated successfully.")
                return redirect('drone_status')
            except Exception as e:
                print(f"An error occurred during save: {e}") # DEBUG
                messages.error(request, f"An error occurred while saving the inspection: {str(e)}")
        else: 
            print("Form is NOT valid.") # DEBUG
            print(form.errors) # DEBUG: แสดงว่า error จากฟอร์มคืออะไร
            messages.error(request, "Please correct the errors shown below.")
    else: # GET request
        form = DroneInspectionForm(instance=inspection)

    return render(request, 'dashboard/edit_inspection.html', {'form': form, 'inspection': inspection})

@login_required
def plant_detail_view(request, plant_id):
    # ดึงเฉพาะโรงไฟฟ้าที่ drone_controller เป็น user นี้เท่านั้น
    plant = get_object_or_404(SolarPlant, id=plant_id, drone_controller=request.user)

    zones = plant.zones.prefetch_related('rows__panels')  # ดึงข้อมูลเชิงลึกแบบ efficient
    return render(request, 'dashboard/plant_detail.html', {
        'plant': plant,
        'zones': zones,
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