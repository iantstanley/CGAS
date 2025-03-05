# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Client, Project, ProjectEmail, ProjectBillingEmail, ProjectPhone,
    PropertyDeed, PropertyMap, ProjectAttachment, ProjectComment, FieldCrew,
    CrewMember, Vehicle, TotalStation, GpsReceiver, DataCollector, MobileHotspot,
    RtkNetwork, GateCode, CalendarEvent, Ordinance
)

# Admin action to force geocode projects
def force_geocode_selected_projects(modeladmin, request, queryset):
    """Admin action to force geocode selected projects"""
    success_count = 0
    for project in queryset:
        if project.force_geocode():
            success_count += 1
    
    if success_count:
        modeladmin.message_user(
            request, 
            f"Successfully geocoded {success_count} out of {queryset.count()} selected projects."
        )
    else:
        modeladmin.message_user(
            request,
            "No projects could be geocoded. Make sure they have valid addresses.",
            level="warning"
        )
force_geocode_selected_projects.short_description = "Force geocode selected projects"

class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'position')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model"""
    list_display = ('project_number', 'title', 'client', 'status', 'geocoded', 'latitude', 'longitude')
    list_filter = ('status', 'geocoded')
    search_fields = ('project_number', 'title', 'client__name')
    actions = [force_geocode_selected_projects]

# Register your models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Client)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectEmail)
admin.site.register(ProjectBillingEmail)
admin.site.register(ProjectPhone)
admin.site.register(PropertyDeed)
admin.site.register(PropertyMap)
admin.site.register(ProjectAttachment)
admin.site.register(ProjectComment)
admin.site.register(FieldCrew)
admin.site.register(CrewMember)
admin.site.register(Vehicle)
admin.site.register(TotalStation)
admin.site.register(GpsReceiver)
admin.site.register(DataCollector)
admin.site.register(MobileHotspot)
admin.site.register(RtkNetwork)
admin.site.register(GateCode)
admin.site.register(CalendarEvent)
admin.site.register(Ordinance)