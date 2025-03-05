# core/models/__init__.py
from core.models.users import User, CustomUserManager
from core.models.clients import Client
from core.models.projects import (
    Project, ProjectEmail, ProjectBillingEmail, ProjectPhone,
    PropertyDeed, PropertyMap, ProjectAttachment, ProjectComment
)
from core.models.field_crews import (
    FieldCrew, CrewMember, Vehicle, TotalStation,
    GpsReceiver, DataCollector, MobileHotspot, RtkNetwork
)
from core.models.resources import GateCode, Ordinance
from core.models.calendar import CalendarEvent