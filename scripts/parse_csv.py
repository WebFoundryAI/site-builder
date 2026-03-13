#!/usr/bin/env python3
"""
Parse CSV input from workflow and output as JSON for matrix strategy.

Expected CSV format (header + rows):
domain,city,service_type,business_name,phone,cf_project,repo_name,areas_radius_miles
bristolemergencyplumber.co.uk,Bristol,Emergency Plumber,Bristol Emergency Plumber,0117 428 0200,bristol-ep,bristol-emergency-plumber,15
"""

import sys
import json
import csv
import os
from io import StringIO

def parse_csv_input():
    csv_content = sys.stdin.read().strip()

    if not csv_content:
        print(json.dumps([]))
        return

    try:
        reader = csv.DictReader(StringIO(csv_content))
        sites = []

        for row in reader:
            if not row.get('domain'):
                continue

            # Validate required fields (cf_project, repo_name, address_line2, service_type are auto-generated)
            required_fields = ['domain', 'city', 'business_name', 'phone', 'address_line1', 'postcode', 'areas_radius_miles']
            missing = [f for f in required_fields if not row.get(f)]

            if missing:
                print(f"ERROR: Missing fields in row: {', '.join(missing)}", file=sys.stderr)
                sys.exit(1)

            # Generate repo_name and cf_project from domain
            # Convert domain to repo name: bristolemergencyplumber.co.uk -> bristol-emergency-plumber-co-uk
            domain_clean = row['domain'].lower().replace('.', '-')
            repo_name = domain_clean
            cf_project = domain_clean

            # address_line2 defaults to city
            address_line2 = row.get('address_line2', row['city'].strip()).strip()

            # service_type will be set during site customization (default: "Emergency Plumber")
            service_type = 'Emergency Plumber'

            # Validate domain format
            if not '.' in row['domain']:
                print(f"ERROR: Invalid domain format: {row['domain']}", file=sys.stderr)
                sys.exit(1)

            # Validate radius is numeric
            try:
                radius = float(row['areas_radius_miles'])
                if radius <= 0:
                    print(f"ERROR: Radius must be positive: {radius}", file=sys.stderr)
                    sys.exit(1)
            except ValueError:
                print(f"ERROR: Invalid radius value: {row['areas_radius_miles']}", file=sys.stderr)
                sys.exit(1)

            sites.append({
                'domain': row['domain'].strip(),
                'city': row['city'].strip(),
                'service_type': service_type,
                'business_name': row['business_name'].strip(),
                'phone': row['phone'].strip() if row.get('phone') else '',
                'address_line1': row['address_line1'].strip(),
                'address_line2': address_line2,
                'postcode': row['postcode'].strip(),
                'cf_project': cf_project,
                'repo_name': repo_name,
                'areas_radius_miles': int(float(row['areas_radius_miles'])),
            })

        # Output as JSON string for GitHub Actions
        json_output = json.dumps(sites)
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/stdout'), 'a') as f:
            f.write(f"sites={json_output}\n")

    except Exception as e:
        print(f"ERROR: Failed to parse CSV: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    parse_csv_input()
