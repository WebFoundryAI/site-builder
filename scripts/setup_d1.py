#!/usr/bin/env python3
"""
Setup Cloudflare D1 database for a new site.
Creates D1 database and initializes schema.
"""

import sys
import json
import argparse
import subprocess
from pathlib import Path

def create_d1_database(project_name: str, account_id: str, api_token: str) -> dict:
    """Create a new D1 database using wrangler."""
    db_name = f"{project_name}-leads"

    print(f"Creating D1 database: {db_name}...", file=sys.stderr)

    try:
        result = subprocess.run(
            ['wrangler', 'd1', 'create', db_name],
            capture_output=True,
            text=True,
            env={
                'CLOUDFLARE_API_TOKEN': api_token,
                'CLOUDFLARE_ACCOUNT_ID': account_id,
            }
        )

        if result.returncode != 0:
            print(f"ERROR: Failed to create D1 database: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        # Parse database ID from output
        # Output format: Created database project-leads with ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        output = result.stdout + result.stderr
        lines = output.split('\n')

        db_id = None
        for line in lines:
            if 'ID:' in line:
                parts = line.split('ID:')
                if len(parts) > 1:
                    db_id = parts[1].strip()
                    break

        if not db_id:
            print("ERROR: Could not extract database ID from wrangler output", file=sys.stderr)
            print(f"Output: {output}", file=sys.stderr)
            sys.exit(1)

        print(f"✓ Created D1 database {db_name} with ID: {db_id}", file=sys.stderr)
        return {'name': db_name, 'id': db_id}

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

def initialize_database_schema(db_id: str, account_id: str, api_token: str):
    """Initialize database schema with leads table."""
    schema_sql = """
    CREATE TABLE IF NOT EXISTS leads (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        service_type TEXT,
        location TEXT,
        message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_email ON leads(email);
    CREATE INDEX IF NOT EXISTS idx_created_at ON leads(created_at DESC);
    """

    print(f"Initializing database schema...", file=sys.stderr)

    try:
        result = subprocess.run(
            ['wrangler', 'd1', 'execute', db_id, '--remote', '--command', schema_sql],
            capture_output=True,
            text=True,
            env={
                'CLOUDFLARE_API_TOKEN': api_token,
                'CLOUDFLARE_ACCOUNT_ID': account_id,
            }
        )

        if result.returncode != 0:
            print(f"WARNING: Schema initialization may have failed: {result.stderr}", file=sys.stderr)
        else:
            print(f"✓ Initialized database schema", file=sys.stderr)

    except Exception as e:
        print(f"WARNING: {str(e)}", file=sys.stderr)

def update_wrangler_toml(db_id: str):
    """Update wrangler.toml with D1 database ID."""
    wrangler_file = Path('wrangler.toml')

    if not wrangler_file.exists():
        print(f"WARNING: wrangler.toml not found", file=sys.stderr)
        return

    content = wrangler_file.read_text()

    # Update or add D1 binding
    if '[[d1_databases]]' in content:
        import re
        content = re.sub(
            r'binding = "DB"[^\n]*\n\s*database_id = "[^"]*"',
            f'binding = "DB"\n  database_id = "{db_id}"',
            content
        )
    else:
        content += f'\n[[d1_databases]]\nbinding = "DB"\ndatabase_id = "{db_id}"\n'

    wrangler_file.write_text(content)
    print(f"✓ Updated wrangler.toml with D1 binding", file=sys.stderr)

def setup_d1(project: str):
    """Setup D1 database for project."""
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')

    if not account_id or not api_token:
        print("ERROR: CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN environment variables required", file=sys.stderr)
        sys.exit(1)

    db = create_d1_database(project, account_id, api_token)
    initialize_database_schema(db['id'], account_id, api_token)
    update_wrangler_toml(db['id'])

    print(f"✓ D1 setup complete", file=sys.stderr)

if __name__ == '__main__':
    import os

    parser = argparse.ArgumentParser(description='Setup Cloudflare D1 database')
    parser.add_argument('--project', required=True, help='Cloudflare project name')

    args = parser.parse_args()
    setup_d1(args.project)
