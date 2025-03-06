# core/models/clients.py
from django.db import models
from django.urls import reverse

class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('builder', 'Builder'),
        ('contractor', 'Contractor'),
        ('municipality', 'Municipality'),
        ('engineer', 'Engineer'),
        ('general_public', 'General Public'),
        ('ncdot', 'NCDOT'),
        ('developer', 'Developer'),
        ('architect', 'Architect'),
        ('utility_company', 'Utility Company'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Client Name')
    company_name = models.CharField(max_length=255, blank=True)
    client_type = models.CharField(
        max_length=50, 
        choices=CLIENT_TYPE_CHOICES,
        blank=True,
        verbose_name='Client Type'
    )
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    billing_email = models.EmailField(blank=True, verbose_name='Billing Contact Email')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.company_name:
            return f"{self.company_name} - {self.name}"
        return self.name
    
    def get_absolute_url(self):
        return reverse('client-detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['name']


class ClientEmail(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField()
    label = models.CharField(max_length=100, blank=True, help_text="E.g., Work, Personal, Assistant")
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.email} ({self.label})" if self.label else self.email
    
    class Meta:
        ordering = ['-is_primary', 'email']


class ClientPhone(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='phones')
    phone = models.CharField(max_length=20)
    label = models.CharField(max_length=100, blank=True, help_text="E.g., Mobile, Office, Home")
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.phone} ({self.label})" if self.label else self.phone
    
    class Meta:
        ordering = ['-is_primary', 'phone']