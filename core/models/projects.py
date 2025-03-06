# core/models/projects.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
import os
import logging

from core.models.clients import Client
from core.models.users import User
from core.utils import geocode_address

logger = logging.getLogger(__name__)

def project_contract_path(instance, filename):
    """File path for contract documents"""
    return f'projects/{instance.project_number}/contracts/{filename}'


def project_attachment_path(instance, filename):
    """File path for project attachments"""
    return f'projects/{instance.project.project_number}/attachments/{filename}'


def project_deed_map_path(instance, filename):
    """File path for deed maps and plats"""
    return f'projects/{instance.project.project_number}/deed_maps/{filename}'


class Project(models.Model):
    """Project model for the CGAS application."""
    # Status Choices - expanded from original
    STATUS_CHOICES = (
        ('admin', 'Admin'),
        ('field_ready', 'Field Ready'),
        ('mapping', 'Mapping'),
        ('pls_review', 'PLS Review'),
        ('on_hold', 'On Hold'),
        ('construction_ongoing', 'Construction Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic Project Information
    project_number = models.CharField(max_length=50, unique=True)  # Removed blank=True to make it required
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='admin')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    # Project Contract Information
    has_legal_contract = models.BooleanField(default=False, verbose_name="Has Legal Contract")
    contract_document = models.FileField(upload_to=project_contract_path, blank=True, null=True)
    legal_name_for_survey = models.CharField(max_length=255, blank=True, null=True, 
                                             verbose_name="Legal Name for Survey Documents")
    
    # Property Information
    property_address = models.TextField(blank=True, null=True, verbose_name="Property Address")
    property_tax_parcel = models.CharField(max_length=100, blank=True, null=True, 
                                           verbose_name="Property Tax Parcel Number")
    flood_map_number = models.CharField(max_length=100, blank=True, null=True)
    flood_zone = models.CharField(max_length=50, blank=True, null=True, verbose_name="Flood Zone")  # Added new field
    base_flood_elevation = models.CharField(max_length=50, blank=True, null=True)
    
    # Geographic Information - NEW FIELDS FOR GIS MODULE
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    geocoded = models.BooleanField(default=False, help_text="Whether this project has been geocoded")
    
    # Financial Information
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quoted_time_frame = models.CharField(max_length=100, blank=True, null=True, 
                                         help_text="e.g., '2 weeks', '1 month'")
    
    # Team Assignment
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    assigned_to = models.ManyToManyField(User, related_name='assigned_projects', blank=True)
    
    # System Fields
    location = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Project Notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project_number} - {self.title}" if self.project_number else self.title
    
    def get_absolute_url(self):
        return reverse('project-detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        """Generate project number if not provided and geocode address"""
        if not self.project_number:
            # Format: CGAS-YEAR-SEQUENCE
            # Example: CGAS-2025-001
            year = self.created_at.year if self.created_at else timezone.now().year
            
            # Find the last project number for this year
            last_project = Project.objects.filter(
                project_number__startswith=f'CGAS-{year}-'
            ).order_by('project_number').last()
            
            if last_project:
                # Extract the sequence number
                try:
                    last_seq = int(last_project.project_number.split('-')[-1])
                    new_seq = last_seq + 1
                except ValueError:
                    new_seq = 1
            else:
                new_seq = 1
                
            self.project_number = f'CGAS-{year}-{new_seq:03d}'
        
        # Geocode address if property address exists and hasn't been geocoded yet
        if not self.geocoded and self.property_address:
            coordinates = geocode_address(
                self.property_address, 
                None,  # No city field in Project model 
                None,  # No state field in Project model
                None   # No zip_code field in Project model
            )
            if coordinates:
                self.latitude, self.longitude = coordinates
                self.geocoded = True
        
        super().save(*args, **kwargs)
    
    def force_geocode(self):
        """
        Force geocoding of this project's address, regardless of current geocoded status
        Returns True if geocoding was successful, False otherwise
        """
        if not self.property_address:
            logger.warning(f"Cannot geocode Project {self.project_number}: No property address")
            return False
        
        logger.info(f"Force geocoding Project {self.project_number}: {self.property_address}")
        
        # Try different address formats to increase chances of success
        address_variations = [
            self.property_address  # Try original address
        ]
        
        # If there's a location field, also try using that
        if self.location and self.location != self.property_address:
            address_variations.append(self.location)
        
        # Add variations with city/state explicitly added if not present
        for location in ["Sunset Beach, NC", "Ocean Isle Beach, NC", "Shallotte, NC"]:
            if location not in self.property_address:
                address_variations.append(f"{self.property_address}, {location}")
        
        # Try each address variation
        for address in address_variations:
            logger.info(f"Trying address variation: {address}")
            coordinates = geocode_address(address)
            if coordinates:
                self.latitude, self.longitude = coordinates
                self.geocoded = True
                self.save(update_fields=['latitude', 'longitude', 'geocoded'])
                logger.info(f"Successfully geocoded Project {self.project_number}")
                return True
        
        logger.error(f"All geocoding attempts failed for Project {self.project_number}")
        return False
    
    class Meta:
        ordering = ['-created_at']


class ProjectEmail(models.Model):
    """Model for storing multiple client emails per project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='client_emails')
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
    
    class Meta:
        unique_together = ['project', 'email']


class ProjectBillingEmail(models.Model):
    """Model for storing multiple billing emails per project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='billing_emails')
    email = models.EmailField()
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return self.email
    
    class Meta:
        unique_together = ['project', 'email']


class ProjectPhone(models.Model):
    """Model for storing multiple client phone numbers per project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='client_phones')
    phone = models.CharField(max_length=20)
    description = models.CharField(max_length=50, blank=True, help_text="e.g., 'Office', 'Mobile'")
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return self.phone


class PropertyDeed(models.Model):
    """Model for storing multiple property deed references"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='property_deeds')
    book = models.CharField(max_length=50)
    page = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Book {self.book}, Page {self.page}"


class PropertyMap(models.Model):
    """Model for storing multiple property plats/maps"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='property_maps')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=project_deed_map_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ProjectAttachment(models.Model):
    """Model for storing project attachments"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=project_attachment_path)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def filename(self):
        return os.path.basename(self.file.name)


class ProjectComment(models.Model):
    """Model for storing project comments"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.user} at {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']