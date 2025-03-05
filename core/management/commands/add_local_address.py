# core/management/commands/add_local_address.py
from django.core.management.base import BaseCommand
import json
import os

class Command(BaseCommand):
    help = 'Add a local address to the geocoding database'

    def add_arguments(self, parser):
        parser.add_argument('address', type=str, help='Address key (e.g., "main st, shallotte")')
        parser.add_argument('lat', type=float, help='Latitude')
        parser.add_argument('lng', type=float, help='Longitude')

    def handle(self, *args, **options):
        address = options['address'].lower()
        lat = options['lat']
        lng = options['lng']
        
        # Path to the JSON file
        file_path = os.path.join('core', 'local_addresses.json')
        
        # Load existing data or create new
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        
        # Add new address
        data[address] = [lat, lng]
        
        # Save back to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f'Added "{address}" at coordinates ({lat}, {lng})'))