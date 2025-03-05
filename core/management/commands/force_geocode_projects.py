# core/management/commands/force_geocode_projects.py
from django.core.management.base import BaseCommand
from core.models import Project
from core.utils import geocode_address
from time import sleep
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Force re-geocode specified projects or all projects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Re-geocode all projects, even those already geocoded',
        )
        parser.add_argument(
            '--ids',
            nargs='+',
            type=int,
            help='Specific project IDs to re-geocode',
        )

    def handle(self, *args, **options):
        if options['ids']:
            projects = Project.objects.filter(id__in=options['ids'])
            self.stdout.write(f"Force geocoding {projects.count()} specific projects")
        elif options['all']:
            projects = Project.objects.all()
            self.stdout.write(f"Force geocoding all {projects.count()} projects")
        else:
            projects = Project.objects.filter(geocoded=False)
            self.stdout.write(f"Geocoding {projects.count()} non-geocoded projects")
        
        success_count = 0
        for i, project in enumerate(projects, 1):
            if project.property_address:
                self.stdout.write(f"Geocoding {i}/{projects.count()}: {project.project_number}")
                
                # Format the address properly for better geocoding results
                address = project.property_address
                # Clean the address a bit if needed
                if ',' not in address and 'NC' not in address and 'North Carolina' not in address:
                    self.stdout.write(f"Enhancing address format for better geocoding")
                    if 'Sunset Beach' in address:
                        address += ', Sunset Beach, NC'
                    elif 'Little River' in address:
                        address += ', Little River, SC'
                    
                # Clear existing coordinates if force geocoding
                if options['all'] or options['ids']:
                    project.geocoded = False
                    
                coordinates = geocode_address(address)
                
                if coordinates:
                    project.latitude, project.longitude = coordinates
                    project.geocoded = True
                    project.save(update_fields=['latitude', 'longitude', 'geocoded'])
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully geocoded {project.project_number}: {coordinates}"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Could not geocode {project.project_number}: {address}"
                    ))
                
                # Be nice to geocoding services with a small delay
                sleep(1)
            else:
                self.stdout.write(self.style.WARNING(
                    f"Project {project.project_number} has no property address"
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f"Geocoding complete: {success_count}/{projects.count()} projects successfully geocoded"
        ))