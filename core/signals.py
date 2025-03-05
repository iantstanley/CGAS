# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Project)
def ensure_project_geocoded(sender, instance, created, **kwargs):
    """Ensure that projects get geocoded after they're saved"""
    if created or not instance.geocoded:
        if instance.property_address and (not instance.latitude or not instance.longitude):
            logger.info(f"Post-save geocoding for Project {instance.project_number}")
            instance.force_geocode()