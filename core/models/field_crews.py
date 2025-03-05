# core/models/field_crews.py
from django.db import models
from django.urls import reverse
from django.utils import timezone

class FieldCrew(models.Model):
    """Model representing a field survey crew"""
    crew_id = models.CharField(max_length=50, verbose_name="Crew ID")
    contact_phone = models.CharField(max_length=20, verbose_name="Contact Phone", blank=True, null=True)
    contact_email = models.EmailField(verbose_name="Contact Email", blank=True, null=True)
    contact_address = models.TextField(verbose_name="Contact Address", blank=True, null=True)
    color = models.CharField(max_length=20, verbose_name="Calendar Color", default="#3788d8")
    notes = models.TextField(verbose_name="Notes", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['crew_id']
        verbose_name = "Field Crew"
        verbose_name_plural = "Field Crews"

    def __str__(self):
        return self.crew_id

    def get_absolute_url(self):
        return reverse('field-crew-detail', kwargs={'pk': self.pk})
        
    def needs_vehicle_maintenance(self):
        """Check if vehicle needs maintenance"""
        if hasattr(self, 'vehicle'):
            return self.vehicle.needs_oil_change() or self.vehicle.needs_tag_renewal()
        return False

class CrewMember(models.Model):
    """Model representing an individual crew member"""
    crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=100, verbose_name="Member Name")
    position = models.CharField(max_length=100, verbose_name="Position", blank=True, null=True)
    phone = models.CharField(max_length=20, verbose_name="Phone", blank=True, null=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    
    def __str__(self):
        return self.name

class Vehicle(models.Model):
    """Model representing a field crew vehicle"""
    crew = models.OneToOneField(FieldCrew, on_delete=models.CASCADE, related_name='vehicle')
    make = models.CharField(max_length=50, verbose_name="Make")
    model = models.CharField(max_length=50, verbose_name="Model")
    year = models.PositiveIntegerField(verbose_name="Year")
    license_plate = models.CharField(max_length=20, verbose_name="License Plate")
    tag_renewal_date = models.DateField(verbose_name="Tag Renewal Date")
    last_oil_change = models.DateField(verbose_name="Last Oil Change Date")
    notes = models.TextField(verbose_name="Vehicle Notes", blank=True, null=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
    
    def needs_oil_change(self):
        """Check if vehicle needs oil change (older than 6 months)"""
        if not self.last_oil_change:
            return False
        six_months_ago = timezone.now().date() - timezone.timedelta(days=180)
        return self.last_oil_change < six_months_ago
    
    def needs_tag_renewal(self):
        """Check if vehicle needs tag renewal (within next 30 days)"""
        if not self.tag_renewal_date:
            return False
        thirty_days_from_now = timezone.now().date() + timezone.timedelta(days=30)
        return self.tag_renewal_date <= thirty_days_from_now

class TotalStation(models.Model):
    """Model representing a Total Station instrument"""
    crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='total_stations')
    model_number = models.CharField(max_length=100, verbose_name="Model Number")
    last_calibration = models.DateField(verbose_name="Last Calibration Date")
    
    def __str__(self):
        return f"{self.model_number}"
    
    def needs_calibration(self):
        """Check if total station needs calibration (older than 1 year)"""
        if not self.last_calibration:
            return False
        one_year_ago = timezone.now().date() - timezone.timedelta(days=365)
        return self.last_calibration < one_year_ago

class GpsReceiver(models.Model):
    """Model representing a GPS Base or Rover"""
    TYPE_CHOICES = [
        ('BASE', 'Base'),
        ('ROVER', 'Rover'),
    ]
    
    crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='gps_receivers')
    model_number = models.CharField(max_length=100, verbose_name="Model Number")
    receiver_type = models.CharField(max_length=5, choices=TYPE_CHOICES, verbose_name="Receiver Type")
    
    def __str__(self):
        return f"{self.get_receiver_type_display()}: {self.model_number}"

class DataCollector(models.Model):
    """Model representing a data collector device"""
    crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='data_collectors')
    model_number = models.CharField(max_length=100, verbose_name="Model Number")
    has_ts_module = models.BooleanField(default=False, verbose_name="Has TS Module")
    has_gps_module = models.BooleanField(default=False, verbose_name="Has GPS Module")
    software_version = models.CharField(max_length=50, verbose_name="SurvCE/PC Version", blank=True, null=True)
    
    def __str__(self):
        return f"{self.model_number}"

class MobileHotspot(models.Model):
    """Model representing a mobile hotspot device"""
    crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='mobile_hotspots')
    make_model = models.CharField(max_length=100, verbose_name="Make/Model")
    phone_number = models.CharField(max_length=20, verbose_name="Phone Number", blank=True, null=True)
    network_name = models.CharField(max_length=50, verbose_name="Network Name")
    network_password = models.CharField(max_length=50, verbose_name="Network Password")
    
    def __str__(self):
        return f"{self.make_model}"

class RtkNetwork(models.Model):
    """Model representing RTK Network login credentials"""
    crew = models.ForeignKey(FieldCrew, on_delete=models.CASCADE, related_name='rtk_networks')
    network_name = models.CharField(max_length=100, verbose_name="Network Name")
    username = models.CharField(max_length=100, verbose_name="Username")
    password = models.CharField(max_length=100, verbose_name="Password")
    
    def __str__(self):
        return f"{self.network_name}"