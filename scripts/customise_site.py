#!/usr/bin/env python3
"""
Customize the Manchester template site with new brand details.
Updates brand.ts, locations.ts, and other critical files.
"""

import sys
import json
import argparse
import re
from pathlib import Path

def customize_brand_file(domain: str, city: str, business_name: str, phone: str,
                        address_line1: str, address_line2: str, postcode: str, template_dir: str = '.'):
    """Update src/data/brand.ts with new site details."""
    brand_file = Path(template_dir) / 'src/data/brand.ts'

    if not brand_file.exists():
        print(f"ERROR: {brand_file} not found", file=sys.stderr)
        sys.exit(1)

    content = brand_file.read_text()

    # Update brand details
    content = re.sub(
        r'brandName: "[^"]*"',
        f'brandName: "{business_name}"',
        content
    )

    content = re.sub(
        r'domain: "[^"]*"',
        f'domain: "{domain}"',
        content
    )

    content = re.sub(
        r'phone: "[^"]*"',
        f'phone: "{phone.replace(" ", "")}"',
        content
    )

    content = re.sub(
        r'phoneFormatted: "[^"]*"',
        f'phoneFormatted: "{phone}"',
        content
    )

    # Update address
    content = re.sub(
        r'addressLine1: "[^"]*"',
        f'addressLine1: "{address_line1}"',
        content
    )

    content = re.sub(
        r'addressLine2: "[^"]*"',
        f'addressLine2: "{address_line2}"',
        content
    )

    content = re.sub(
        r'postcode: "[^"]*"',
        f'postcode: "{postcode}"',
        content
    )

    # Email based on domain
    email = f"info@{domain}"
    content = re.sub(
        r'email: "[^"]*"',
        f'email: "{email}"',
        content
    )

    brand_file.write_text(content)
    print(f"✓ Updated brand.ts", file=sys.stderr)

def customize_locations_file(city: str, template_dir: str = '.'):
    """Update src/data/locations.ts with new primary location."""
    locations_file = Path(template_dir) / 'src/data/locations.ts'

    if not locations_file.exists():
        print(f"ERROR: {locations_file} not found", file=sys.stderr)
        sys.exit(1)

    # For now, keep the Manchester locations structure
    # In production, would call location service to get coordinates for new city
    print(f"✓ Kept locations.ts (manual location setup required for {city})", file=sys.stderr)

def customize_service_areas(city: str, service_areas_file: str):
    """Update service areas from generated file."""
    if not Path(service_areas_file).exists():
        print(f"WARNING: Service areas file not found: {service_areas_file}", file=sys.stderr)
        return

    with open(service_areas_file) as f:
        areas = json.load(f)

    print(f"✓ Loaded service areas: {areas.get('count', 0)} areas for {city}", file=sys.stderr)

def customize_config_files(domain: str, template_dir: str = '.'):
    """Update astro.config.mjs and other config files."""
    config_file = Path(template_dir) / 'astro.config.mjs'

    if config_file.exists():
        content = config_file.read_text()
        content = re.sub(
            r"site: 'https://[^']*/'",
            f"site: 'https://{domain}/'",
            content
        )
        config_file.write_text(content)
        print(f"✓ Updated astro.config.mjs", file=sys.stderr)

def customize_site(domain: str, city: str, business_name: str, phone: str,
                   address_line1: str, address_line2: str, postcode: str,
                   service_areas: str, service_type: str, template_dir: str = '.'):
    """Main customization function."""
    print(f"Customizing site for {business_name} ({domain})...", file=sys.stderr)

    try:
        customize_brand_file(domain, city, business_name, phone, address_line1, address_line2, postcode, template_dir)
        customize_locations_file(city, template_dir)
        customize_config_files(domain, template_dir)
        customize_service_areas(city, service_areas)

        print(f"✓ Site customization complete", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: Customization failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Customize R2R template site')
    parser.add_argument('--domain', required=True, help='New domain')
    parser.add_argument('--city', required=True, help='City name')
    parser.add_argument('--business-name', required=True, help='Business name')
    parser.add_argument('--phone', required=True, help='Business phone')
    parser.add_argument('--address-line1', required=True, help='Address line 1')
    parser.add_argument('--address-line2', required=True, help='Address line 2')
    parser.add_argument('--postcode', required=True, help='Postcode')
    parser.add_argument('--service-areas', required=True, help='Service areas JSON file')
    parser.add_argument('--service-type', required=True, help='Service type')
    parser.add_argument('--template-dir', default='.', help='Template directory (default: current directory)')

    args = parser.parse_args()
    customize_site(
        args.domain,
        args.city,
        args.business_name,
        args.phone,
        args.address_line1,
        args.address_line2,
        args.postcode,
        args.service_areas,
        args.service_type,
        args.template_dir
    )
