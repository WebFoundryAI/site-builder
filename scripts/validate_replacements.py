#!/usr/bin/env python3
"""
Validate that parsed sites have all required fields for successful customization.
Checks that domain, city, phone, and other critical fields are present.
"""

import sys
import json

def validate_sites():
    sites_json = sys.stdin.read().strip()

    if not sites_json:
        print("ERROR: No sites data provided", file=sys.stderr)
        sys.exit(1)

    try:
        sites = json.loads(sites_json)

        if not isinstance(sites, list):
            print("ERROR: Sites must be a JSON array", file=sys.stderr)
            sys.exit(1)

        if not sites:
            print("WARNING: No sites provided", file=sys.stderr)
            return

        # Validate each site
        for i, site in enumerate(sites):
            errors = []

            # Required fields validation
            if not site.get('domain'):
                errors.append('domain is required')
            elif not all(c in 'abcdefghijklmnopqrstuvwxyz0123456789.-' for c in site['domain'].lower()):
                errors.append('domain contains invalid characters')

            if not site.get('city'):
                errors.append('city is required')

            if not site.get('business_name'):
                errors.append('business_name is required')

            if not site.get('phone'):
                errors.append('phone is required')

            if not site.get('cf_project'):
                errors.append('cf_project is required')

            if not site.get('repo_name'):
                errors.append('repo_name is required')

            # Validate repo_name format (alphanumeric, hyphens, underscores)
            if site.get('repo_name'):
                if not all(c in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in site['repo_name'].lower()):
                    errors.append('repo_name contains invalid characters (use alphanumeric, hyphens, underscores)')

            if not isinstance(site.get('areas_radius_miles'), (int, float)):
                errors.append('areas_radius_miles must be a number')
            elif site.get('areas_radius_miles', 0) <= 0:
                errors.append('areas_radius_miles must be positive')

            if errors:
                print(f"ERROR in site {i} ({site.get('domain', 'unknown')}): {'; '.join(errors)}", file=sys.stderr)
                sys.exit(1)

        print(f"✓ Validated {len(sites)} site(s) successfully")

    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON format: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    validate_sites()
