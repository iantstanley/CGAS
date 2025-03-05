# core/urls.py
from django.urls import path
from . import views, views_gis
from django.conf import settings
from django.conf.urls.static import static
from .views_gis import project_data_json, force_geocode_projects
from .views import (
    OrdinanceListView, OrdinanceDetailView, OrdinanceCreateView,
    OrdinanceUpdateView, OrdinanceDeleteView, OrdinanceRedirectView
)

urlpatterns = [
    # Home/Dashboard URL
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Client URLs
    path('clients/', views.ClientListView.as_view(), name='client-list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client-detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client-delete'),
    
    # Project URLs - Main CRUD
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/add/', views.ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='project-delete'),
    path('projects/<int:pk>/print/', views.ProjectPrintView.as_view(), name='project-print'),
    
    # Project URLs - Related items management
    # Email management
    path('projects/<int:pk>/add-email/', views.add_project_email, name='project-add-email'),
    path('projects/<int:pk>/delete-email/<int:email_id>/', views.delete_project_email, name='project-delete-email'),
    
    # Billing email management
    path('projects/<int:pk>/add-billing-email/', views.add_project_billing_email, name='project-add-billing-email'),
    path('projects/<int:pk>/delete-billing-email/<int:email_id>/', views.delete_project_billing_email, name='project-delete-billing-email'),
    
    # Phone management
    path('projects/<int:pk>/add-phone/', views.add_project_phone, name='project-add-phone'),
    path('projects/<int:pk>/delete-phone/<int:phone_id>/', views.delete_project_phone, name='project-delete-phone'),
    
    # Property deed management
    path('projects/<int:pk>/add-deed/', views.add_property_deed, name='project-add-deed'),
    path('projects/<int:pk>/delete-deed/<int:deed_id>/', views.delete_property_deed, name='project-delete-deed'),
    
    # Property map management
    path('projects/<int:pk>/add-map/', views.add_property_map, name='project-add-map'),
    path('projects/<int:pk>/delete-map/<int:map_id>/', views.delete_property_map, name='project-delete-map'),
    
    # Attachment management
    path('projects/<int:pk>/add-attachment/', views.add_project_attachment, name='project-add-attachment'),
    path('projects/<int:pk>/delete-attachment/<int:attachment_id>/', views.delete_project_attachment, name='project-delete-attachment'),
    
    # Comment management
    path('projects/<int:pk>/add-comment/', views.add_project_comment, name='project-add-comment'),
    
    # Field Crew URLs - Main CRUD
    path('field-crews/', views.FieldCrewListView.as_view(), name='field-crew-list'),
    path('field-crews/add/', views.FieldCrewCreateView.as_view(), name='field-crew-create'),
    path('field-crews/<int:pk>/', views.FieldCrewDetailView.as_view(), name='field-crew-detail'),
    path('field-crews/<int:pk>/edit/', views.FieldCrewUpdateView.as_view(), name='field-crew-update'),
    path('field-crews/<int:pk>/delete/', views.FieldCrewDeleteView.as_view(), name='field-crew-delete'),
    
    # Field Crew URLs - Related items management
    # Crew members management
    path('field-crews/<int:pk>/add-member/', views.add_crew_member, name='field-crew-add-member'),
    path('field-crews/<int:pk>/delete-member/<int:member_id>/', views.delete_crew_member, name='field-crew-delete-member'),
    
    # Vehicle management
    path('field-crews/<int:pk>/add-vehicle/', views.add_vehicle, name='field-crew-add-vehicle'),
    
    # Total Station management
    path('field-crews/<int:pk>/add-total-station/', views.add_total_station, name='field-crew-add-total-station'),
    path('field-crews/<int:pk>/delete-total-station/<int:station_id>/', views.delete_total_station, name='field-crew-delete-total-station'),
    
    # GPS Receiver management
    path('field-crews/<int:pk>/add-gps-receiver/', views.add_gps_receiver, name='field-crew-add-gps-receiver'),
    path('field-crews/<int:pk>/delete-gps-receiver/<int:receiver_id>/', views.delete_gps_receiver, name='field-crew-delete-gps-receiver'),
    
    # Data Collector management
    path('field-crews/<int:pk>/add-data-collector/', views.add_data_collector, name='field-crew-add-data-collector'),
    path('field-crews/<int:pk>/delete-data-collector/<int:collector_id>/', views.delete_data_collector, name='field-crew-delete-data-collector'),
    
    # Mobile Hotspot management
    path('field-crews/<int:pk>/add-hotspot/', views.add_mobile_hotspot, name='field-crew-add-hotspot'),
    path('field-crews/<int:pk>/delete-hotspot/<int:hotspot_id>/', views.delete_mobile_hotspot, name='field-crew-delete-hotspot'),
    
    # RTK Network management
    path('field-crews/<int:pk>/add-rtk-network/', views.add_rtk_network, name='field-crew-add-rtk-network'),
    path('field-crews/<int:pk>/delete-rtk-network/<int:network_id>/', views.delete_rtk_network, name='field-crew-delete-rtk-network'),
    
    # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('password-reset/', 
     views.CustomPasswordResetView.as_view(), 
     name='password_reset'),
    path('password-reset/done/', 
        views.CustomPasswordResetDoneView.as_view(), 
        name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        views.CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('password-reset-complete/', 
        views.CustomPasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),

    # Field Resources URLs - Gate Codes
    path('field-resources/', views.GateCodeListView.as_view(), name='gate-code-list'),
    path('field-resources/add/', views.GateCodeCreateView.as_view(), name='gate-code-create'),
    path('field-resources/<int:pk>/edit/', views.GateCodeUpdateView.as_view(), name='gate-code-update'),
    path('field-resources/<int:pk>/delete/', views.GateCodeDeleteView.as_view(), name='gate-code-delete'),
    
    # Calendar URLs - Main Calendar View
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    
    # Calendar Event URLs - Main CRUD
    path('calendar/events/add/', views.CalendarEventCreateView.as_view(), name='calendar-event-create'),
    path('calendar/events/<int:pk>/', views.CalendarEventDetailView.as_view(), name='calendar-event-detail'),
    path('calendar/events/<int:pk>/edit/', views.CalendarEventUpdateView.as_view(), name='calendar-event-update'),
    path('calendar/events/<int:pk>/delete/', views.CalendarEventDeleteView.as_view(), name='calendar-event-delete'),
    
    # Calendar API endpoints for AJAX operations
    path('calendar/events/json/', views.CalendarEventListView.as_view(), name='calendar-events-json'),
    path('calendar/events/resize/', views.calendar_event_resize, name='calendar-event-resize'),
    path('calendar/events/drop/', views.calendar_event_drop, name='calendar-event-drop'),
    path('calendar/events/quick-add/', views.quick_add_calendar_event, name='calendar-quick-add-event'),

    path('ordinances/', OrdinanceListView.as_view(), name='ordinance-list'),
    path('ordinances/<int:pk>/', OrdinanceDetailView.as_view(), name='ordinance-detail'),
    path('ordinances/new/', OrdinanceCreateView.as_view(), name='ordinance-create'),
    path('ordinances/<int:pk>/edit/', OrdinanceUpdateView.as_view(), name='ordinance-update'),
    path('ordinances/<int:pk>/delete/', OrdinanceDeleteView.as_view(), name='ordinance-delete'),
    path('ordinances/<int:pk>/view/', OrdinanceRedirectView.as_view(), name='ordinance-redirect'),

    path('map/', views_gis.ProjectMapView.as_view(), name='project-map'),
    path('api/project-data/', views_gis.project_data_json, name='project-data-json'),

    path('api/projects/map-data/', project_data_json, name='project-data-json'),
    path('projects/force-geocode/', force_geocode_projects, name='force-geocode-projects'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)