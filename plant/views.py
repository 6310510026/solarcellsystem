from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from drone.models import DroneInspection
from .forms import SolarPlantForm
from .models import SolarPlant


# Create your views here.
@login_required
def create_plant(request):
    if request.method == 'POST':
        form = SolarPlantForm(request.POST, user=request.user)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.owner = request.user
            plant.save()
            return redirect('plant_list')
    else:
        form = SolarPlantForm(user=request.user)
    return render(request, 'dashboard/create_plant.html', {'form': form})


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

