# drone/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DroneInspection
from .forms import DroneInspectionForm

# =============================
# DRONE CONTROLLER: Upload View
# =============================
@login_required
def upload_inspection(request):
    if request.user.role != 'drone_controller':
        return redirect('no_permission')

    if request.method == 'POST':
        form = DroneInspectionForm(request.POST, request.FILES)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.captured_by = request.user
            inspection.save()
            messages.success(request, "อัปโหลดภาพเรียบร้อยแล้ว")
            return redirect('drone_status')
    else:
        form = DroneInspectionForm()

    return render(request, 'dashboard/upload_inspection.html', {'form': form})

@login_required
def drone_status_view(request):
    if request.user.role != 'drone_controller':
        return redirect('no_permission')

    inspections = DroneInspection.objects.filter(captured_by=request.user).order_by('-captured_at')
    return render(request, 'dashboard/status.html', {'inspections': inspections})


