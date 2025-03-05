# core/views_gis.py
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.db.models import Count
from .models import Project
import logging
import json

logger = logging.getLogger(__name__)

class ProjectMapView(LoginRequiredMixin, TemplateView):
    template_name = 'gis/project_map.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add stats to context
        total_projects = Project.objects.count()
        geocoded_projects = Project.objects.filter(latitude__isnull=False, longitude__isnull=False).count()
        context['total_projects'] = total_projects
        context['geocoded_projects'] = geocoded_projects
        
        # Get status counts - useful for debugging
        status_counts = Project.objects.values('status').annotate(count=Count('id'))
        context['status_counts'] = {item['status']: item['count'] for item in status_counts}
        
        return context

def project_data_json(request):
    """API endpoint to get project data for the map"""
    projects = Project.objects.filter(latitude__isnull=False, longitude__isnull=False)
    
    # Log how many projects we're sending to the map
    project_count = projects.count()
    logger.info(f"Sending {project_count} geocoded projects to the map")
    
    data = []
    for project in projects:
        try:
            data.append({
                'id': project.id,
                'project_number': project.project_number,
                'client_name': project.client.name,
                'title': project.title,
                'address': project.property_address or "No address provided",
                'latitude': float(project.latitude),
                'longitude': float(project.longitude),
                'status': project.status,
                'url': f"/projects/{project.id}/"
            })
        except Exception as e:
            logger.error(f"Error processing project {project.id}: {e}")
    
    return JsonResponse(data, safe=False)

def force_geocode_projects(request):
    """View to force geocode all projects"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('project-map')
    
    # Get all projects without geocoding
    projects = Project.objects.filter(latitude__isnull=True, longitude__isnull=True)
    
    success_count = 0
    for project in projects:
        if project.property_address:
            success = project.force_geocode()
            if success:
                success_count += 1
    
    # Also try to geocode projects that previously failed
    failed_projects = Project.objects.filter(geocoded=False, property_address__isnull=False)
    for project in failed_projects:
        success = project.force_geocode()
        if success:
            success_count += 1
    
    messages.success(request, f"Successfully geocoded {success_count} projects.")
    
    # If there are still non-geocoded projects, inform the user
    remaining = Project.objects.filter(latitude__isnull=True, longitude__isnull=True).count()
    if remaining > 0:
        messages.warning(request, f"There are still {remaining} projects without geocoding. Check your project addresses.")
    
    return redirect('project-map')