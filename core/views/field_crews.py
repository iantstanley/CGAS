# core/views/field_crews.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from core.models import (
    FieldCrew, CrewMember, Vehicle, TotalStation, GpsReceiver,
    DataCollector, MobileHotspot, RtkNetwork
)
from core.forms import (
    FieldCrewForm, FieldCrewSearchForm, CrewMemberForm, VehicleForm,
    TotalStationForm, GpsReceiverForm, DataCollectorForm,
    MobileHotspotForm, RtkNetworkForm
)

class FieldCrewListView(LoginRequiredMixin, ListView):
    model = FieldCrew
    template_name = 'field_crews/field_crew_list.html'
    context_object_name = 'field_crews'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = FieldCrew.objects.all()
        form = FieldCrewSearchForm(self.request.GET)
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search')
            
            if search_term:
                queryset = queryset.filter(
                    Q(crew_id__icontains=search_term) |
                    Q(contact_phone__icontains=search_term) |
                    Q(contact_email__icontains=search_term) |
                    Q(members__name__icontains=search_term)
                ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = FieldCrewSearchForm(self.request.GET)
        return context

class FieldCrewDetailView(LoginRequiredMixin, DetailView):
    model = FieldCrew
    template_name = 'field_crews/field_crew_detail.html'
    context_object_name = 'field_crew'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add upcoming events for this field crew
        today = timezone.now().date()
        two_weeks_later = today + timedelta(days=14)
        context['upcoming_events'] = self.object.calendar_events.filter(
            start_time__date__gte=today,
            start_time__date__lte=two_weeks_later
        ).order_by('start_time')
        return context

class FieldCrewCreateView(LoginRequiredMixin, CreateView):
    model = FieldCrew
    template_name = 'field_crews/field_crew_form.html'
    form_class = FieldCrewForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Field Crew created successfully!')
        return response

class FieldCrewUpdateView(LoginRequiredMixin, UpdateView):
    model = FieldCrew
    template_name = 'field_crews/field_crew_form.html'
    form_class = FieldCrewForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Field Crew updated successfully!')
        return response

class FieldCrewDeleteView(LoginRequiredMixin, DeleteView):
    model = FieldCrew
    template_name = 'field_crews/field_crew_confirm_delete.html'
    success_url = reverse_lazy('field-crew-list')
    context_object_name = 'field_crew'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Field Crew deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Additional Field Crew-related Views
@login_required
def add_crew_member(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = CrewMemberForm(request.POST)
        
        if form.is_valid():
            crew_member = form.save(commit=False)
            crew_member.crew = field_crew
            crew_member.save()
            messages.success(request, 'Crew member added successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def delete_crew_member(request, pk, member_id):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    crew_member = get_object_or_404(CrewMember, pk=member_id, crew=field_crew)
    crew_member.delete()
    messages.success(request, 'Crew member removed successfully!')
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def add_vehicle(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        
        if form.is_valid():
            # Check if the crew already has a vehicle
            if hasattr(field_crew, 'vehicle'):
                # Update existing vehicle
                for key, value in form.cleaned_data.items():
                    setattr(field_crew.vehicle, key, value)
                field_crew.vehicle.save()
            else:
                # Create new vehicle
                vehicle = form.save(commit=False)
                vehicle.crew = field_crew
                vehicle.save()
                
            messages.success(request, 'Vehicle information updated successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def add_total_station(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = TotalStationForm(request.POST)
        
        if form.is_valid():
            total_station = form.save(commit=False)
            total_station.crew = field_crew
            total_station.save()
            messages.success(request, 'Total Station added successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def delete_total_station(request, pk, station_id):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    total_station = get_object_or_404(TotalStation, pk=station_id, crew=field_crew)
    total_station.delete()
    messages.success(request, 'Total Station removed successfully!')
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def add_gps_receiver(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = GpsReceiverForm(request.POST)
        
        if form.is_valid():
            gps_receiver = form.save(commit=False)
            gps_receiver.crew = field_crew
            gps_receiver.save()
            messages.success(request, 'GPS Receiver added successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def delete_gps_receiver(request, pk, receiver_id):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    gps_receiver = get_object_or_404(GpsReceiver, pk=receiver_id, crew=field_crew)
    gps_receiver.delete()
    messages.success(request, 'GPS Receiver removed successfully!')
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def add_data_collector(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = DataCollectorForm(request.POST)
        
        if form.is_valid():
            data_collector = form.save(commit=False)
            data_collector.crew = field_crew
            data_collector.save()
            messages.success(request, 'Data Collector added successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def delete_data_collector(request, pk, collector_id):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    data_collector = get_object_or_404(DataCollector, pk=collector_id, crew=field_crew)
    data_collector.delete()
    messages.success(request, 'Data Collector removed successfully!')
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def add_mobile_hotspot(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = MobileHotspotForm(request.POST)
        
        if form.is_valid():
            mobile_hotspot = form.save(commit=False)
            mobile_hotspot.crew = field_crew
            mobile_hotspot.save()
            messages.success(request, 'Mobile Hotspot added successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def delete_mobile_hotspot(request, pk, hotspot_id):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    mobile_hotspot = get_object_or_404(MobileHotspot, pk=hotspot_id, crew=field_crew)
    mobile_hotspot.delete()
    messages.success(request, 'Mobile Hotspot removed successfully!')
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def add_rtk_network(request, pk):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    
    if request.method == 'POST':
        form = RtkNetworkForm(request.POST)
        
        if form.is_valid():
            rtk_network = form.save(commit=False)
            rtk_network.crew = field_crew
            rtk_network.save()
            messages.success(request, 'RTK Network credentials added successfully!')
        
    return redirect('field-crew-detail', pk=field_crew.pk)

@login_required
def delete_rtk_network(request, pk, network_id):
    field_crew = get_object_or_404(FieldCrew, pk=pk)
    rtk_network = get_object_or_404(RtkNetwork, pk=network_id, crew=field_crew)
    rtk_network.delete()
    messages.success(request, 'RTK Network credentials removed successfully!')
    return redirect('field-crew-detail', pk=field_crew.pk)