# populate_gate_codes.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cgas_project.settings')
django.setup()

from core.models import GateCode

# Gate codes to add
gate_codes = [
    {"community_name": "HB Dunescape", "gate_code": "1943", "notes": "Just Numbers"},
    {"community_name": "HB Oyster Harbour", "gate_code": "4224", "notes": "Just Numbers"},
    {"community_name": "HB West Gate", "gate_code": "#6100"},
    {"community_name": "Sea Watch", "gate_code": "#3184", "notes": "Sunset Harbor Entrance"},
    {"community_name": "St. James Passcode", "gate_code": "862572"},
    {"community_name": "Brunswick Storage", "gate_code": "1959"},
    {"community_name": "Brantley Circle (Brick Landing)", "gate_code": "2882"},
    {"community_name": "Bent Tree", "gate_code": "#4438"},
    {"community_name": "Palm Cove (SSB East)", "gate_code": "3860#"},
    {"community_name": "Ocean Harbour Estates", "gate_code": "# or * 8467", "notes": "let me know which is correct"},
    {"community_name": "Harbour Watch (Calabash)", "gate_code": "8467"},
    {"community_name": "Kingfish Bay", "gate_code": "5464"},
    {"community_name": "OIB East (The Pointe)", "gate_code": "#3626"},
    {"community_name": "OIB West Gate", "gate_code": "2424"},
    {"community_name": "Ibis Bay", "gate_code": "1492"},
    {"community_name": "River Run Plantation", "gate_code": "#0977"},
    {"community_name": "Riverside Drive", "gate_code": "52455"},
    {"community_name": "Cape Fear Jetport (Skydiving Gate)", "gate_code": "1230"},
    {"community_name": "CG Storage Unit @ Brunswick Storage", "gate_code": "Gate Code #3387*, unit #110 (outside unit)"}
]

# Add gate codes to database
def populate_gate_codes():
    for code_data in gate_codes:
        GateCode.objects.get_or_create(
            community_name=code_data["community_name"],
            gate_code=code_data["gate_code"],
            notes=code_data.get("notes", "")
        )
    print(f"Added {len(gate_codes)} gate codes to the database.")

if __name__ == '__main__':
    print("Starting gate code population...")
    populate_gate_codes()
    print("Gate code population complete!")