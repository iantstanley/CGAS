# core/utils.py
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging
import json
import os
from time import sleep

logger = logging.getLogger(__name__)

# Local address database - add your common areas with known coordinates
LOCAL_ADDRESSES = {
    # Format: 'street, city, state': (latitude, longitude)
    'hen cove ave, shallotte': (33.9308, -78.3903),  # Example coordinates - replace with actual
    'ocean isle beach': (33.8943, -78.4269),
    'sunset beach': (33.8813, -78.5122),
    'little river sc': (33.8729, -78.6326),
    'southport': (33.924048, -78.020886),
    'supply': (34.016685, -78.269217),
    'holden beach': (33.922417, -78.282717),
    'calabash': (33.893850, -78.561986),
    'leland': (34.239561, -78.009386),
    'ash': (34.059278, -78.521980),
}

def geocode_address(address, city=None, state=None, zip_code=None):
    """
    Convert an address to latitude and longitude
    Returns tuple of (latitude, longitude) or None if geocoding fails
    """
    if not address:
        logger.warning("Cannot geocode: Empty address provided")
        return None
        
    # Create full address string
    full_address = address.strip()
    if city and state:
        full_address = f"{address.strip()}, {city.strip()}, {state.strip()}"
        if zip_code:
            full_address += f" {zip_code.strip()}"
    
    # Check local address database first - case insensitive search
    full_address_lower = full_address.lower()
    for local_addr, coords in LOCAL_ADDRESSES.items():
        if local_addr in full_address_lower:
            logger.info(f"Found address in local database: {full_address} -> {coords}")
            return coords
    
    # Basic address cleanup to avoid redundancy
    # Remove duplicate city/state entries
    if "shallotte, nc, shallotte" in full_address.lower():
        full_address = full_address.lower().replace("shallotte, nc, shallotte", "shallotte, nc")
    
    if "north carolina" in full_address.lower() and "nc" in full_address.lower():
        full_address = full_address.replace("North Carolina", "").replace("north carolina", "")

    logger.info(f"Attempting to geocode address: {full_address}")
    
    # Initialize geocoder with custom user agent and longer timeout
    geolocator = Nominatim(user_agent="coastal_geomatics_admin", timeout=15)
    
    # Try to geocode with retry logic
    for attempt in range(3):
        try:
            # First attempt: Try with the full address
            location = geolocator.geocode(
                full_address,
                exactly_one=True,
                country_codes="us"
            )
            
            if location:
                logger.info(f"Geocoding succeeded: {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            
            # Second attempt: Try with a simplified address
            if attempt == 0:
                # Extract street and city only
                parts = full_address.split(',')
                if len(parts) >= 2:
                    street = parts[0].strip()
                    city = parts[1].strip()
                    simplified = f"{street}, {city}"
                    
                    logger.info(f"Trying simplified address: {simplified}")
                    location = geolocator.geocode(
                        simplified,
                        exactly_one=True,
                        country_codes="us"
                    )
                    
                    if location:
                        logger.info(f"Geocoding succeeded with simplified address: {location}")
                        return (location.latitude, location.longitude)
            
            # Third attempt: Try with regional context
            if attempt == 1:
                # Try with Brunswick County regional context
                brunswick_address = f"{full_address.split(',')[0]}, Brunswick County, NC"
                logger.info(f"Trying with county context: {brunswick_address}")
                location = geolocator.geocode(
                    brunswick_address,
                    exactly_one=True,
                    country_codes="us"
                )
                
                if location:
                    logger.info(f"Geocoding succeeded with county context: {location}")
                    return (location.latitude, location.longitude)
            
            # Log the failure
            logger.warning(f"Could not geocode address: {full_address}")
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"Geocoding attempt {attempt+1} failed: {str(e)}")
            if attempt < 2:
                sleep(2)  # Longer wait before retry
            continue
        except Exception as e:
            logger.error(f"Unexpected error during geocoding: {str(e)}")
            if attempt < 2:
                sleep(2)
            continue
    
    logger.error(f"All geocoding attempts failed for: {full_address}")
    return None