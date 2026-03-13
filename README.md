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
domain,city,service_type,business_name,phone,address_line1,address_line2,postcode,cf_project,areas_radius_miles
bristolemergencyplumber.co.uk,Bristol,Emergency Plumber,Bristol Emergency Plumber,0117 428 0200,Unit 2 Broad Street,Bristol,BS1 2HF,bristol-ep,15
cardiffplumber.co.uk,Cardiff,24-Hour Plumber,Cardiff 24 Hour Plumber,029 2037 0100,10 The Hayes,Cardiff,CF10 1AH,cardiff-24h,12
```

**Column Definitions:**

| Column | Description | Example |
|--------|-------------|---------|
| `domain` | Full domain for new site | `bristolemergencyplumber.co.uk` |
| `city` | Primary city served | `Bristol` |
| `service_type` | Service category (displayed on all pages) | `Emergency Plumber` or `Blocked Drains` |
| `business_name` | Business legal name | `Bristol Emergency Plumber` |
| `phone` | Business phone with spaces/formatting | `0117 428 0200` |
| `address_line1` | Business address line 1 | `Unit 2 Broad Street` |
| `address_line2` | Business address line 2 (city/town) | `Bristol` |
| `postcode` | Business postcode | `BS1 2HF` |
| `cf_project` | Cloudflare Pages project name (alphanumeric + hyphen) | `bristol-ep` |
| `areas_radius_miles` | Service radius from city center (integer) | `15` |

**Auto-Generated:**
- `repo_name` — Automatically generated from domain with `-co-uk` suffix (e.g., `bristolemergencyplumber.co.uk` → `bristol-emergency-plumber-co-uk`)

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
domain,city,service_type,business_name,phone,address_line1,address_line2,postcode,cf_project,areas_radius_miles
bristolemergencyplumber.co.uk,Bristol,Emergency Plumber,Bristol Emergency Plumber,0117 428 0200,Unit 2 Broad Street,Bristol,BS1 2HF,bristol-ep,15
cardiffplumber.co.uk,Cardiff,24-Hour Plumber,Cardiff 24 Hour Plumber,029 2037 0100,10 The Hayes,Cardiff,CF10 1AH,cardiff-24h,12
leedsdrainunblock.co.uk,Leeds,Blocked Drains,Leeds Drain Unblock,0113 468 9300,Sovereign House,Leeds,LS1 4BJ,leeds-du,15
manchesteremergency.co.uk,Manchester,Emergency Plumber,Manchester Emergency Plumber,0161 282 8080,Unit 1 Stockport Road,Manchester,M12 6DF,manchester-ep,18
birminghamdrains.co.uk,Birmingham,Blocked Drains,Birmingham Drains,0121 555 0100,27 Newhall Street,Birmingham,B3 1HQ,birmingham-d,14
edinburghplumber.co.uk,Edinburgh,Emergency Plumber,Edinburgh Emergency Plumber,0131 226 8080,12 Multrees Walk,Edinburgh,EH2 3DQ,edinburgh-ep,12
glasgowdrains.co.uk,Glasgow,Blocked Drains,Glasgow Drain Unblock,0141 285 5656,123 Sauchiehall Street,Glasgow,G2 3HQ,glasgow-d,13
liverplumber.co.uk,Liverpool,Emergency Plumber,Liverpool Emergency Plumber,0151 707 8080,8 Cook Street,Liverpool,L2 3QP,liverpool-ep,11
newcastleplumber.co.uk,Newcastle,24-Hour Plumber,Newcastle 24 Hour Plumber,0191 500 0100,Collingwood House,Newcastle,NE1 1TF,newcastle-24h,10
nottinghamdrains.co.uk,Nottingham,Blocked Drains,Nottingham Blocked Drains,0115 847 0000,51 High Street,Nottingham,NG1 2AP,nottingham-d,14
sheffieldplumber.co.uk,Sheffield,Emergency Plumber,Sheffield Emergency Plumber,0114 275 0100,123 West Street,Sheffield,S1 4EJ,sheffield-ep,12
coventryplumber.co.uk,Coventry,24-Hour Plumber,Coventry 24 Hour Plumber,024 7660 0700,9 Little Park Street,Coventry,CV1 2UR,coventry-24h,11
leicesterdrain.co.uk,Leicester,Blocked Drains,Leicester Drain Unblock,0116 222 0100,61 High Street,Leicester,LE1 4BP,leicester-d,12
bristoldrain.co.uk,Bristol,Blocked Drains,Bristol Blocked Drains,0117 428 0200,Unit 2 Broad Street,Bristol,BS1 2HF,bristol-d,15
londonemergency.co.uk,London,Emergency Plumber,London Emergency Plumber,020 7078 8202,123 Bond Street,London,W1S 1AZ,london-ep,20
stokeplumber.co.uk,Stoke-on-Trent,24-Hour Plumber,Stoke-on-Trent 24 Hour Plumber,01782 550 0100,Etruria Vale,Stoke-on-Trent,ST4 7BF,stoke-24h,12
```

**Auto-generated repo names:**
- bristolemergencyplumber.co.uk → `bristol-emergency-plumber-co-uk`
- cardiffplumber.co.uk → `cardiff-plumber-co-uk`
- leedsdrainunblock.co.uk → `leeds-drain-unblock-co-uk`
- (and so on for all 15 sites)

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
