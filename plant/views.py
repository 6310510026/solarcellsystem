from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from decimal import Decimal
from drone.models import DroneInspection
from .forms import SolarPlantForm, ZoneForm, PanelRowForm, SolarPanelForm
from .models import SolarPlant, Zone, PanelRow, SolarPanel, InspectionReport


# Create your views here.
@login_required
def create_plant(request):
    if request.method == 'POST':
        form = SolarPlantForm(request.POST)
        if form.is_valid():
            plant = form.save(commit=False)  # ยังไม่บันทึก
            plant.owner = request.user       # กำหนด owner
            plant.save()                     # บันทึกลง DB
            return redirect('create_zone', plant_id=plant.id)
    else:
        form = SolarPlantForm()
    return render(request, 'dashboard/create_plant.html', {'form': form})


@login_required
def create_zone(request, plant_id):
    plant = get_object_or_404(SolarPlant, id=plant_id)
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.plant = plant
            zone.save()
            return redirect('create_panel_row', zone_id=zone.id)
    else:
        form = ZoneForm()
    return render(request, 'dashboard/create_zone.html', {'form': form, 'plant_id': plant.id})

@login_required
def create_panel_row(request, zone_id):
    zone = get_object_or_404(Zone, id=zone_id)
    plant_id = zone.plant.id  # ดึง plant_id จาก zone

    if request.method == 'POST':
        form = PanelRowForm(request.POST)
        if form.is_valid():
            panel_row = form.save(commit=False)
            panel_row.zone = zone
            panel_row.save()
            return redirect('create_solar_panel', panel_row_id=panel_row.id)
    else:
        form = PanelRowForm()
        
    return render(request, 'dashboard/create_panel_row.html', {
        'form': form,
        'zone_id': zone.id,
        'plant_id': plant_id,
    })


@login_required
def create_solar_panel(request, panel_row_id):
    panel_row = get_object_or_404(PanelRow, id=panel_row_id)
    if request.method == 'POST':
        form = SolarPanelForm(request.POST)
        if form.is_valid():
            solar_panel = form.save(commit=False)
            solar_panel.row = panel_row
            solar_panel.save()
            return redirect('plant_list')
    else:
        form = SolarPanelForm()

    context = {
        'form': form,
        'panel_row_id': panel_row.id,
        'zone_id': panel_row.zone.id,
    }
    return render(request, 'dashboard/create_solar_panel.html', context)


@login_required
def plant_list_view(request):
    plants = SolarPlant.objects.filter(owner=request.user)
    return render(request, 'dashboard/plant_list.html', {'plants': plants})

@login_required
def delete_plant(request, pk):
    plant = get_object_or_404(SolarPlant, pk=pk, owner=request.user)
    if request.method == 'POST':
        plant.delete()
        messages.success(request, 'Plant deleted successfully.')
        return redirect('plant_list')
    return render(request, 'dashboard/delete_plant.html', {'plant': plant})

@login_required
def edit_plant(request, pk):
    plant = get_object_or_404(SolarPlant, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = SolarPlantForm(request.POST, instance=plant, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plant updated successfully.')
            return redirect('plant_detail_solar', pk=plant.id)
    else:
        form = SolarPlantForm(instance=plant, user=request.user)
    return render(request, 'dashboard/edit_plant.html', {'form': form, 'plant': plant})

@login_required
def plant_detail_view(request, pk):
    plant = get_object_or_404(SolarPlant, pk=pk)
    panel_rows = PanelRow.objects.filter(zone__plant=plant).order_by('row_number')
    panels_by_row = {}

    max_columns = 0
    for row in panel_rows:
        panels = SolarPanel.objects.filter(row=row)
        panels_by_row[row.row_number] = {panel.column_number: panel for panel in panels}
        max_columns = max(max_columns, panels.count())

    context = {
        'plant': plant,
        'panels_by_row': panels_by_row,
        'columns_range': range(1, max_columns + 1),
    }
    return render(request, 'dashboard/plant_detail_solar.html', context)

@login_required
def plant_report_view(request):
    plants = SolarPlant.objects.filter(owner=request.user)
    plant_reports = []

    for plant in plants:
        report = InspectionReport.objects.filter(plant=plant, is_analyzed=True).last()
        plant_reports.append({
            'plant': plant,
            'report_ready': report is not None,
            'report': report
        })

    context = {'plant_reports': plant_reports}
    return render(request, 'dashboard/plant_report.html', context)

@login_required
def view_report(request, report_id):
    report = get_object_or_404(InspectionReport, id=report_id)
    context = {
        'report': report,
        'pie_data': {
            'labels': ['Red Zone', 'Yellow Zone', 'Green Zone'],
            'values': [report.redzone, report.yellowzone, report.greenzone]
        }
    }
    return render(request, 'dashboard/view_report.html', context)


