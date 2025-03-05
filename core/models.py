# core/models.py
# This file now defines migration-critical functions directly
# and imports all models from their specific modules for backward compatibility
import os

# Define path helper functions directly in this module for migration compatibility
def project_contract_path(instance, filename):
    """File path for contract documents"""
    return f'projects/{instance.project_number}/contracts/{filename}'

def project_attachment_path(instance, filename):
    """File path for project attachments"""
    return f'projects/{instance.project.project_number}/attachments/{filename}'

def project_deed_map_path(instance, filename):
    """File path for deed maps and plats"""
    return f'projects/{instance.project.project_number}/deed_maps/{filename}'

def project_contract_path(instance, filename):
    return f'projects/{instance.project_number}/contracts/{filename}'

# Then import all models
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