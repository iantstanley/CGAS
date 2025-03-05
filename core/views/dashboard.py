# core/views/dashboard.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from core.models import Project, Client, FieldCrew, GateCode, Ordinance, CalendarEvent

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_projects_count'] = Project.objects.filter(
            status__in=['in_progress', 'field_ready', 'mapping', 'construction_ongoing']
        ).count()
        context['clients_count'] = Client.objects.count()
        context['recent_projects'] = Project.objects.all().order_by('-created_at')[:5]
        context['field_crews_count'] = FieldCrew.objects.count()
        context['gate_codes_count'] = GateCode.objects.count()
        context['ordinances_count'] = Ordinance.objects.count()
        
        # Get upcoming calendar events for dashboard
        today = timezone.now().date()
        one_week_later = today + timedelta(days=7)
        context['upcoming_events'] = CalendarEvent.objects.filter(
            start_time__date__gte=today,
            start_time__date__lte=one_week_later
        ).order_by('start_time')[:5]
        
        # Get field crews with maintenance alerts
        field_crews_with_alerts = []
        for crew in FieldCrew.objects.all():
            if crew.needs_vehicle_maintenance():
                field_crews_with_alerts.append(crew)
                if len(field_crews_with_alerts) >= 3:  # Limit to 3 for dashboard
                    break
        
        context['field_crews_with_alerts'] = field_crews_with_alerts
        return context