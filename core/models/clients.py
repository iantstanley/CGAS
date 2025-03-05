# core/models/clients.py
from django.db import models
from django.urls import reverse

class Client(models.Model):
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
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