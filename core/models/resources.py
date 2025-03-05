# core/models/resources.py
from django.db import models
from django.urls import reverse
import os

class GateCode(models.Model):
    """Model representing a gate code for a private community"""
    community_name = models.CharField(max_length=255, verbose_name="Community Name")
    gate_code = models.CharField(max_length=50, verbose_name="Gate Code")
    notes = models.TextField(verbose_name="Notes", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['community_name']
        verbose_name = "Gate Code"
        verbose_name_plural = "Gate Codes"

    def __str__(self):
        return f"{self.community_name}: {self.gate_code}"

    def get_absolute_url(self):
        return reverse('gate-code-list')

class Ordinance(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the municipality or community")
    description = models.TextField(blank=True, null=True, help_text="Optional description or notes about this ordinance")
    is_url = models.BooleanField(default=False, help_text="Whether this is a web link or a PDF document")
    url = models.URLField(blank=True, null=True, help_text="Website URL if this is a web link")
    document = models.FileField(upload_to='ordinances/', blank=True, null=True, help_text="PDF document if this is not a web link")
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ordinance-detail', args=[str(self.id)])
    
    def get_document_name(self):
        if self.document:
            return os.path.basename(self.document.name)
        return None
    
    class Meta:
        ordering = ['name']
        verbose_name = "Ordinance"
        verbose_name_plural = "Ordinances"