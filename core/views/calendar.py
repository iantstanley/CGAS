# core/views/calendar.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse  # Add reverse import here
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import json

from core.models import CalendarEvent, FieldCrew, Project
from core.forms import CalendarEventForm

# Rest of the file remains unchanged

class CalendarView(LoginRequiredMixin, TemplateView):
    """Main calendar display view"""
    template_name = 'calendar/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['field_crews'] = FieldCrew.objects.all()
        context['projects'] = Project.objects.filter(
            status__in=['admin', 'field_ready', 'in_progress', 'mapping', 'construction_ongoing']
        )
        return context

class CalendarEventListView(LoginRequiredMixin, View):
    """JSON API endpoint for FullCalendar to get events"""
    def get(self, request, *args, **kwargs):
        start = request.GET.get('start')
        end = request.GET.get('end')
        field_crew_id = request.GET.get('field_crew')
        
        # Filter events by date range if provided
        events = CalendarEvent.objects.all()
        if start:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            events = events.filter(end_time__gte=start_date)
        if end:
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
            events = events.filter(start_time__lte=end_date)
        if field_crew_id:
            events = events.filter(field_crew_id=field_crew_id)
        
        # Format events for FullCalendar
        event_list = []
        for event in events:
            event_data = {
                'id': event.id,
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'allDay': event.all_day,
                'color': event.get_color(),
                'extendedProps': {
                    'location': event.location or '',
                    'notes': event.notes or ''
                }
            }
            
            # Add project info if available
            if event.project:
                event_data['extendedProps']['project_number'] = event.project.project_number
                event_data['extendedProps']['project_title'] = event.project.title
                event_data['extendedProps']['project_id'] = event.project.id
                event_data['url'] = reverse('project-detail', args=[event.project.id])
            
            # Add field crew info if available
            if event.field_crew:
                event_data['extendedProps']['field_crew_id'] = event.field_crew.id
                event_data['extendedProps']['field_crew_name'] = event.field_crew.crew_id
            
            event_list.append(event_data)
        
        return JsonResponse(event_list, safe=False)

class CalendarEventCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new calendar event"""
    model = CalendarEvent
    form_class = CalendarEventForm
    template_name = 'calendar/calendar_event_form.html'
    success_url = reverse_lazy('calendar')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Calendar event created successfully!')
        return response
    
    def get_initial(self):
        initial = super().get_initial()
        # Pre-populate project field if passed in URL
        project_id = self.request.GET.get('project')
        if project_id:
            try:
                initial['project'] = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                pass
        
        # Pre-populate field crew if passed in URL
        field_crew_id = self.request.GET.get('field_crew')
        if field_crew_id:
            try:
                initial['field_crew'] = FieldCrew.objects.get(pk=field_crew_id)
            except FieldCrew.DoesNotExist:
                pass
        
        # Pre-populate start time if passed in URL
        start_time = self.request.GET.get('start')
        if start_time:
            try:
                initial['start_time'] = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        # Pre-populate end time if passed in URL
        end_time = self.request.GET.get('end')
        if end_time:
            try:
                initial['end_time'] = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                pass
        
        return initial

class CalendarEventUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing calendar event"""
    model = CalendarEvent
    form_class = CalendarEventForm
    template_name = 'calendar/calendar_event_form.html'
    success_url = reverse_lazy('calendar')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Calendar event updated successfully!')
        return response

class CalendarEventDetailView(LoginRequiredMixin, DetailView):
    """View for displaying calendar event details"""
    model = CalendarEvent
    template_name = 'calendar/calendar_event_detail.html'
    context_object_name = 'event'

class CalendarEventDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a calendar event"""
    model = CalendarEvent
    template_name = 'calendar/calendar_event_confirm_delete.html'
    success_url = reverse_lazy('calendar')
    context_object_name = 'event'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Calendar event deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def calendar_event_resize(request):
    """AJAX endpoint for handling event resizing in the calendar"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            start_time = data.get('start')
            end_time = data.get('end')
            
            event = get_object_or_404(CalendarEvent, pk=event_id)
            
            # Update event times
            event.start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            event.end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            event.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def calendar_event_drop(request):
    """AJAX endpoint for handling event dragging in the calendar"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            start_time = data.get('start')
            end_time = data.get('end')
            all_day = data.get('allDay', False)
            
            event = get_object_or_404(CalendarEvent, pk=event_id)
            
            # Update event times
            event.start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            event.end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            event.all_day = all_day
            event.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def quick_add_calendar_event(request):
    """AJAX endpoint for quickly creating events from the calendar interface"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            start_time = data.get('start')
            end_time = data.get('end')
            all_day = data.get('allDay', False)
            field_crew_id = data.get('field_crew_id')
            project_id = data.get('project_id')
            
            # Create event
            event = CalendarEvent(
                title=title,
                start_time=datetime.fromisoformat(start_time.replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(end_time.replace('Z', '+00:00')),
                all_day=all_day,
                created_by=request.user
            )
            
            # Add project if provided
            if project_id:
                try:
                    event.project = Project.objects.get(pk=project_id)
                except Project.DoesNotExist:
                    pass
            
            # Add field crew if provided
            if field_crew_id:
                try:
                    event.field_crew = FieldCrew.objects.get(pk=field_crew_id)
                except FieldCrew.DoesNotExist:
                    pass
            
            event.save()
            
            # Return the created event data for the calendar
            event_data = {
                'id': event.id,
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'allDay': event.all_day,
                'color': event.get_color()
            }
            
            return JsonResponse({'status': 'success', 'event': event_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)