# core/management/commands/geocode_projects.py
from django.core.management.base import BaseCommand
from core.models import Project
from core.utils import geocode_address
from time import sleep

class Command(BaseCommand):
    help = 'Geocode all projects that have not been geocoded yet'

    def handle(self, *args, **options):
        projects = Project.objects.filter(geocoded=False)
        total = projects.count()
        
        self.stdout.write(f"Found {total} projects to geocode")
        
        success_count = 0
        for i, project in enumerate(projects, 1):
            if project.property_address:
                self.stdout.write(f"Geocoding {i}/{total}: {project.project_number}")
                
                coordinates = geocode_address(
                    project.property_address, 
                    project.city if hasattr(project, 'city') else None,
                    project.state if hasattr(project, 'state') else None,
                    project.zip_code if hasattr(project, 'zip_code') else None
                )
                
                if coordinates:
                    project.latitude, project.longitude = coordinates
                    project.geocoded = True
                    project.save(update_fields=['latitude', 'longitude', 'geocoded'])
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully geocoded {project.project_number}"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Could not geocode {project.project_number}"
                    ))
                
                # Be nice to geocoding services with a small delay
                sleep(1)
        
        self.stdout.write(self.style.SUCCESS(
            f"Geocoding complete: {success_count}/{total} projects successfully geocoded"
        ))