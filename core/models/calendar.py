# core/models/calendar.py
from django.db import models
from django.urls import reverse

from core.models.users import User
from core.models.projects import Project
from core.models.field_crews import FieldCrew

class CalendarEvent(models.Model):
    """Model representing a calendar event for scheduling field crews and projects"""
    title = models.CharField(max_length=255, verbose_name="Event Title")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='calendar_events', 
                               blank=True, null=True, verbose_name="Related Project")
    field_crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='calendar_events',
                                  blank=True, null=True, verbose_name="Assigned Field Crew")
    start_time = models.DateTimeField(verbose_name="Start Time")
    end_time = models.DateTimeField(verbose_name="End Time")
    all_day = models.BooleanField(default=False, verbose_name="All Day Event")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Location")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events',
                                 verbose_name="Created By")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('calendar-event-detail', kwargs={'pk': self.pk})
    
    def get_color(self):
        """Return the color for this event based on the field crew"""
        if self.field_crew and self.field_crew.color:
            return self.field_crew.color
        # Default colors based on crew_id if available
        if self.field_crew:
            crew_id = self.field_crew.crew_id.lower()
            if 'admin' in crew_id:
                return '#3498db'  # Blue
            elif '1' in crew_id:
                return '#e74c3c'  # Pink/Red
            elif '2' in crew_id:
                return '#9b59b6'  # Purple
            elif '3' in crew_id:
                return '#f39c12'  # Orange
            elif '4' in crew_id:
                return '#2ecc71'  # Green
            elif '5' in crew_id:
                return '#f1c40f'  # Yellow
        return '#3788d8'  # Default FullCalendar blue