#!/usr/bin/env python3
"""
Generate service areas for a given city using postcodes.io API.
Finds all postcode areas within specified radius of city center.
"""

import sys
import json
import argparse
import urllib.request
import urllib.error

def get_postcode_for_city(city: str) -> dict:
    """Get postcode data for a city using postcodes.io API."""
    try:
        # Use postcodes.io to find postcode areas for the city
        url = f"https://api.postcodes.io/postcodes?q={city}&limit=1"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        if data['status'] != 200 or not data['result']:
            print(f"ERROR: Could not find postcode for city: {city}", file=sys.stderr)
            sys.exit(1)

        return data['result'][0]

    except urllib.error.URLError as e:
        print(f"ERROR: Failed to query postcodes.io: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

def get_nearby_areas(latitude: float, longitude: float, radius_miles: int) -> list:
    """Get postcode areas within radius of coordinates."""
    try:
        # Convert miles to kilometers (postcodes.io uses km)
        radius_km = round(radius_miles * 1.60934)

        url = f"https://api.postcodes.io/postcodes?lon={longitude}&lat={latitude}&radius={radius_km}&limit=100"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        if data['status'] != 200 or not data['result']:
            return []

        # Extract unique postcode areas (first part of postcode)
        areas = set()
        for result in data['result']:
            postcode = result['postcode']
            area = postcode.split()[0]  # Get first part (e.g. M1 from M1 1AA)
            if len(area) > 0:
                areas.add(area)

        return sorted(list(areas))

    except Exception as e:
        print(f"WARNING: Failed to get nearby areas: {str(e)}", file=sys.stderr)
        return []

def generate_service_areas(city: str, radius_miles: int, output_file: str, postcode: str = None):
    """Generate and save service areas JSON."""
    print(f"Generating service areas for {city} (radius: {radius_miles} miles)...", file=sys.stderr)

    # Get city center coordinates
    if postcode:
        # Use provided postcode for coordinates
        try:
            url = f"https://api.postcodes.io/postcodes/{postcode.replace(' ', '')}"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())

            if data['status'] != 200 or not data['result']:
                print(f"WARNING: Could not find postcode {postcode}, falling back to city name lookup", file=sys.stderr)
                city_data = get_postcode_for_city(city)
            else:
                city_data = data['result']
        except Exception as e:
            print(f"WARNING: Postcode lookup failed ({str(e)}), falling back to city name", file=sys.stderr)
            city_data = get_postcode_for_city(city)
    else:
        city_data = get_postcode_for_city(city)

    latitude = city_data['latitude']
    longitude = city_data['longitude']

    print(f"Found {city} at coordinates: {latitude}, {longitude}", file=sys.stderr)

    # Get nearby postcode areas
    areas = get_nearby_areas(latitude, longitude, radius_miles)

    print(f"Found {len(areas)} postcode areas within {radius_miles} miles", file=sys.stderr)

    # Save as JSON
    service_areas = {
        'city': city,
        'latitude': latitude,
        'longitude': longitude,
        'radius_miles': radius_miles,
        'postcode_areas': areas,
        'count': len(areas),
    }

    with open(output_file, 'w') as f:
        json.dump(service_areas, f, indent=2)

    print(f"✓ Service areas saved to {output_file}", file=sys.stderr)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate service areas for a city')
    parser.add_argument('--city', required=True, help='City name')
    parser.add_argument('--radius', type=int, required=True, help='Radius in miles')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    parser.add_argument('--postcode', help='Optional: postcode for city center (for more accurate coordinates)')

    args = parser.parse_args()
    generate_service_areas(args.city, args.radius, args.output, args.postcode)
