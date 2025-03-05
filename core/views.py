# core/views.py
# This file is now kept for backward compatibility
# Import all views from their respective modules

from core.views.dashboard import DashboardView
from core.views.auth import (
    CustomLoginView, CustomLogoutView, RegisterView,
    CustomPasswordResetView, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)
from core.views.clients import (
    ClientListView, ClientDetailView, ClientCreateView,
    ClientUpdateView, ClientDeleteView
)
from core.views.projects import (
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView, ProjectPrintView,
    add_project_email, delete_project_email,
    add_project_billing_email, delete_project_billing_email,
    add_project_phone, delete_project_phone,
    add_property_deed, delete_property_deed,
    add_property_map, delete_property_map,
    add_project_attachment, delete_project_attachment,
    add_project_comment
)
from core.views.field_crews import (
    FieldCrewListView, FieldCrewDetailView, FieldCrewCreateView,
    FieldCrewUpdateView, FieldCrewDeleteView,
    add_crew_member, delete_crew_member,
    add_vehicle, add_total_station, delete_total_station,
    add_gps_receiver, delete_gps_receiver,
    add_data_collector, delete_data_collector,
    add_mobile_hotspot, delete_mobile_hotspot,
    add_rtk_network, delete_rtk_network
)
from core.views.calendar import (
    CalendarView, CalendarEventListView, CalendarEventCreateView,
    CalendarEventUpdateView, CalendarEventDetailView, CalendarEventDeleteView,
    calendar_event_resize, calendar_event_drop, quick_add_calendar_event
)
from core.views.resources import (
    GateCodeListView, GateCodeCreateView, GateCodeUpdateView, GateCodeDeleteView,
    OrdinanceListView, OrdinanceDetailView, OrdinanceCreateView,
    OrdinanceUpdateView, OrdinanceDeleteView, OrdinanceRedirectView
)