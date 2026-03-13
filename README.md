# R2R Site Builder — Automated Multi-Site Provisioning

Automated pipeline for provisioning new R2R (Responsive, Reliable, Reusable) plumber service sites from the Manchester template.

## Overview

This GitHub Actions workflow automates the process of cloning and customizing the R2R template site (`WebFoundryAI/manchester_blocked_drain_co_uk`) for new cities and regions. It provisions:

- **Branded Astro website** with domain, business name, phone, address, and service areas
- **Cloudflare Pages deployment** with auto-builds from GitHub
- **Cloudflare D1 database** for lead capture and contact form submissions
- **Dynamic routes** for 100+ pages: services, locations, service×location combos, blog posts
- **Auto-updating sitemap** for SEO
- **GitHub repository** under WebFoundryAI org with CI/CD pre-configured

## Quick Start

### Step 1: Create CSV with Site Details

Create `sites/provision.csv` with one row per site:

```csv
domain,city,business_name,phone,address_line1,postcode,areas_radius_miles
BlockedDrainsAberdeen.co.uk,Aberdeen,Blocked Drains Aberdeen,0800 611 8150,1 Berry Street,AB25 1HF,20
blockeddrainsinaldershot.co.uk,Aldershot,Blocked Drains in Aldershot,0800 30 77 008,14-40 Victoria Rd,GU11 1TQ,20
```

**Column Definitions:**

| Column | Description | Example |
|--------|-------------|---------|
| `domain` | Full domain for new site | `BlockedDrainsAberdeen.co.uk` |
| `city` | Primary city served | `Aberdeen` |
| `business_name` | Business legal name | `Blocked Drains Aberdeen` |
| `phone` | Business phone (can be blank) | `0800 611 8150` |
| `address_line1` | Business address line 1 | `1 Berry Street` |
| `postcode` | Business postcode | `AB25 1HF` |
| `areas_radius_miles` | Service radius from city center (integer) | `20` |

**Auto-Generated:**
- `address_line2` — City name (from `city` column)
- `service_type` — "Emergency Plumber" (set during site customization)
- `cf_project` — Cloudflare Pages project name (e.g., `BlockedDrainsAberdeen.co.uk` → `blocked-drains-aberdeen-co-uk`)
- `repo_name` — GitHub repository name (e.g., `BlockedDrainsAberdeen.co.uk` → `blocked-drains-aberdeen-co-uk`)

### Step 2: Commit CSV to Repository

```bash
git add sites/provision.csv
git commit -m "Add sites for batch provisioning"
git push
```

### Step 3: Trigger Workflow

1. Go to **Actions** → **Provision R2R Sites**
2. Click **Run workflow**
3. Leave `csv_content` **blank** (it will read from `sites/provision.csv`)
4. Set `max_parallel` to number of sites (e.g., `15` for all 15 sites at once)
5. Click **Run workflow**

✓ All sites provision in parallel — ~10-15 minutes total

### Step 4: Monitor Progress

- Watch **Actions** tab for job progress
- Check **WebFoundryAI** org for new repos (bristol-emergency-plumber, cardiff-plumber-24, etc.)
- Each repo will show real-time build status in its Actions tab

## Workflow Architecture

### Two-Job Pipeline

**1. parse-and-validate** (runs once)
- Reads CSV from `sites/provision.csv` or manual input
- Validates all required fields
- Outputs JSON array for matrix strategy

**2. provision** (runs per site with configurable parallelism)
- Clones manchester_blocked_drain_co_uk template
- Generates service areas (postcodes.io within radius)
- Customizes site with brand, domain, address, phone
- Creates Cloudflare Pages project + domain
- Creates D1 database + schema
- Commits and pushes to new GitHub repo
- Sets GitHub secrets

### Max Parallel

- Default: `2` (prevents rate limiting)
- For 15 sites: set to `15`
- Maximum: `20` (GitHub API limits)

## Scripts Overview

### Python Scripts

**`parse_csv.py`**
- Reads CSV from stdin (file or manual input)
- Validates all required fields
- Outputs JSON array for matrix strategy

**`validate_replacements.py`**
- Validates parsed JSON structure
- Checks domain/repo_name/postcode formats
- Ensures all numeric values are valid

**`generate_service_areas.py`**
- Uses postcodes.io API to find city center coordinates
- Queries nearby postcodes within specified radius
- Returns up to 100 postcode areas

**`customise_site.py`**
- Updates `src/data/brand.ts` (domain, phone, business_name, address, postcode)
- Updates `astro.config.mjs` (site URL)
- Loads service areas JSON
- Prepares site for build

**`setup_d1.py`**
- Creates D1 database via wrangler CLI
- Initializes schema (leads table)
- Updates wrangler.toml with database ID

### Shell Scripts

**`setup_cloudflare_pages.sh`**
- Creates Cloudflare Pages project via API
- Configures build command (bun run build)
- Adds custom domain to project

**`set_github_secrets.sh`**
- Sets GitHub repository secrets:
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`
  - `GITHUB_TOKEN` (optional)

## Configuration

### Prerequisites

Set these GitHub secrets at **organization level** (WebFoundryAI):

- `CLOUDFLARE_API_TOKEN` — API token with Pages + D1 permissions
- `CLOUDFLARE_ACCOUNT_ID` — Your Cloudflare account ID
- `GITHUB_TOKEN` — GitHub PAT with repo + workflow scopes

### Workflow Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `csv_content` | (empty) | CSV text (paste here OR commit to sites/provision.csv) |
| `max_parallel` | `2` | Max parallel jobs (1-20) |

## Example: Provisioning 15 Sites

```csv
domain,city,business_name,phone,address_line1,postcode,areas_radius_miles
BlockedDrainsAberdeen.co.uk,Aberdeen,Blocked Drains Aberdeen,0800 611 8150,1 Berry Street,AB25 1HF,20
blockeddrainsinaldershot.co.uk,Aldershot,Blocked Drains in Aldershot,0800 30 77 008,14-40 Victoria Rd,GU11 1TQ,20
plumbersbasildon247.co.uk,Basildon,Plumbers Basildon 247,01268 744500,7 High Pavement,SS14 1EA,20
plumbersbasingstoke.co.uk,Basingstoke,Plumbers Basingstoke,01256 840777,35/41 Essex Road,RG21 7TB,20
PlumbersBournemouth247.co.uk,Bournemouth,Plumbers Bournemouth 247,02380 111200,10 Poole Hill,BH2 5PS,20
DrainBustersBurnley.co.uk,Burnley,Drain Busters Burnley,0121 555 0100,Elm Street Business Park,BB10 1PD,20
burtonupontrentplumbers.co.uk,Burton upon Trent,Burton upon Trent Plumbers,01283 500100,Curzon Street,DE14 2DH,20
plumberschelmsford247.co.uk,Chelmsford,Plumbers Chelmsford 247,01245 203555,Criterion House 40 Parkway,CM2 7PN,20
emergencyplumbercolchester.co.uk,Colchester,Emergency Plumber Colchester,01206 548833,1 George Williams Way,CO1 2JS,20
PlumbErinDarlington.co.uk,Darlington,Plumber in Darlington,0113 468 9300,20 Woodland Road,DL3 7PL,20
drainclearancedoncaster.co.uk,Doncaster,Drain Clearance Doncaster,01302 368686,22-28 Wood Street,DN1 3LW,20
blockeddrainscleareddundee.co.uk,Dundee,Blocked Drains Cleared Dundee,01382 225517,18 South Tay Street,DD1 1PD,20
emergencyplumberexeter.co.uk,Exeter,Emergency Plumber Exeter,01392 354800,48 Queen Street,EX4 3SR,20
emergencyplumberfife.co.uk,Fife,Emergency Plumber Fife,01592 280000,123 High Street,KY2 8NS,18
plumbersgateshead.co.uk,Gateshead,Plumbers Gateshead,0191 500 0100,10 Team Valley,NE11 0BQ,15
```

All fields auto-generated:
- `address_line2` → City name
- `service_type` → "Emergency Plumber"
- `cf_project` → Domain with dots replaced by hyphens
- `repo_name` → Same as cf_project

**Process:**
1. Commit this CSV to `sites/provision.csv`
2. Trigger workflow with `max_parallel=15`
3. All 15 sites build in parallel (~15 minutes)
4. Check WebFoundryAI org for 15 new repos

## Supported Services

Template includes pre-configured services:
- Emergency Plumber
- 24-Hour Plumber
- Boiler Repair
- Blocked Drains

Each service has sub-services. New sites inherit all and generate ~100+ pages automatically.

## Post-Provisioning

After workflow completes:

1. **DNS Configuration**: Point domain to Cloudflare (nameservers shown in Pages project)
2. **Google Search Console**: Add domain and submit sitemap
3. **Google Indexing API**: (Optional) Use batch indexing script for key pages
4. **Contact Form**: D1 database is ready for lead capture

## Troubleshooting

### CSV Validation Errors
- Ensure all required columns are present
- No leading/trailing spaces
- Valid domain format (e.g., no spaces)
- Numeric radius values

### Cloudflare Pages Creation Fails
- Verify API token has Pages permissions
- Check project name doesn't already exist
- Ensure account ID is correct

### GitHub Repo Creation Fails
- Verify GITHUB_TOKEN has repo + workflow scopes
- Check repo name doesn't already exist
- Confirm org has creation permissions

### D1 Database Setup Fails
- Verify wrangler is installed
- Check account has D1 quota
- Review wrangler.toml format

## References

- **Template**: https://github.com/WebFoundryAI/manchester_blocked_drain_co_uk
- **Live Demo**: https://manchesterblockeddrain.co.uk
- **Postcodes.io**: https://postcodes.io
- **Cloudflare API**: https://developers.cloudflare.com
- **Astro**: https://docs.astro.build
