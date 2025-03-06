# core/models/__init__.py
# Import all models so they're available when importing from core.models

# Import existing models
from .users import User
from .clients import Client, ClientEmail, ClientPhone  # Add the new models here
from .projects import (
    Project, ProjectEmail, ProjectPhone, ProjectBillingEmail,
    PropertyDeed, PropertyMap, ProjectAttachment, ProjectComment
)
from .field_crews import (
    FieldCrew, CrewMember, Vehicle, TotalStation,
    GpsReceiver, DataCollector, MobileHotspot, RtkNetwork
)
from .resources import GateCode, Ordinance
from .calendar import CalendarEvent

# Make them all accessible at the core.models level
__all__ = [
    'User',
    'Client', 'ClientEmail', 'ClientPhone',  # Add the new models here
    'Project', 'ProjectEmail', 'ProjectPhone', 'ProjectBillingEmail',
    'PropertyDeed', 'PropertyMap', 'ProjectAttachment', 'ProjectComment',
    'FieldCrew', 'CrewMember', 'Vehicle', 'TotalStation',
    'GpsReceiver', 'DataCollector', 'MobileHotspot', 'RtkNetwork',
    'GateCode', 'Ordinance',
    'CalendarEvent',
]