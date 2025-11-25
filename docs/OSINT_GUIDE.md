# OSINT & Reconnaissance Guide

## Overview

WilsonsRaider now includes **comprehensive OSINT (Open Source Intelligence)** capabilities with:
- Google Dorking automation
- Free/open-source API integrations
- Government & public data sources
- Unified OSINT aggregator

**Cost**: $0-5/month (all tools use free tiers!)

---

## Quick Start

```python
from core.managers.osint_aggregator import OSINTAggregator

# Initialize aggregator
osint = OSINTAggregator()

# Run comprehensive reconnaissance
report = osint.comprehensive_recon("example.com")

print(f"Found {len(report['subdomains'])} subdomains")
print(f"Found {len(report['live_hosts'])} live hosts")
print(f"Found {len(report['urls'])} archived URLs")
print(f"Technologies: {report['technologies']}")

# Export report
report_file = osint.export_report(report, format="markdown")
```

---

## OSINT Tools & Data Sources

### **1. Google Dorking** (`core/tools/google_dorks_wrapper.py`)

**FREE**: 100 queries/day (Google Custom Search API)

**Capabilities**:
- 10 pre-built dork categories
- Automated subdomain discovery
- Exposed file detection
- Login page discovery
- Admin panel detection
- Error message hunting
- API endpoint discovery
- Credential exposure detection (sensitive!)

**Pre-Built Dork Categories**:
1. **exposed_files**: PDF, DOC, XLS, SQL, ENV, Config, Log, Backup files
2. **login_pages**: Login, signin, auth pages
3. **admin_panels**: Admin, administrator, cpanel, dashboard
4. **error_messages**: Stack traces, exceptions, fatal errors
5. **directory_listings**: Index of, directory listing
6. **subdomains**: Site:*.domain
7. **exposed_databases**: SQL dumps, phpMyAdmin
8. **api_endpoints**: API paths, documentation
9. **git_exposure**: .git folders
10. **aws_keys**: AWS access keys (AKIA pattern)

**Usage Examples**:

```python
from core.tools.google_dorks_wrapper import GoogleDorksWrapper

dorks = GoogleDorksWrapper()

# Run all dorks on a domain
results = dorks.dork_site("example.com", category="all")

# Run specific category
admin_panels = dorks.dork_site("example.com", category="admin_panels")

# Find subdomains
subdomains = dorks.find_subdomains("example.com")

# Find exposed files
files = dorks.find_exposed_files("example.com", file_types=['pdf', 'doc', 'sql'])

# Find login pages
logins = dorks.find_login_pages("example.com")

# Custom dork query
results = dorks.search('site:example.com filetype:pdf "confidential"')
```

**Rate Limiting**:
- Free tier: 100 queries/day
- Auto rate limiting: 2 seconds between requests
- Respects Google's terms of service

---

### **2. Free OSINT APIs** (`core/tools/osint_apis_wrapper.py`)

**ALL FREE** (no API key or free tiers)

#### **Certificate Transparency (crt.sh)**
- **FREE**: Unlimited
- **Features**: Find all SSL certificates for a domain
- **Use**: Subdomain discovery

```python
from core.tools.osint_apis_wrapper import OSINTAPIsWrapper

osint = OSINTAPIsWrapper()

# Search certificates
certs = osint.crtsh_search("example.com")
# Returns: List of certificates with subdomains
```

#### **DNS Lookups**
- **FREE**: Unlimited
- **Features**: A, AAAA, MX, NS, TXT, CNAME records

```python
# DNS lookup
a_records = osint.dns_lookup("example.com", "A")
mx_records = osint.dns_lookup("example.com", "MX")
txt_records = osint.dns_lookup("example.com", "TXT")
```

#### **WHOIS Lookups**
- **FREE**: Unlimited (command-line)
- **Features**: Domain registration info, registrar, dates, nameservers

```python
# WHOIS lookup
whois_data = osint.whois_lookup("example.com")
# Returns: {registrar, creation_date, expiration_date, name_servers}
```

#### **IP Geolocation (ip-api.com)**
- **FREE**: 45 requests/minute
- **Features**: Country, city, ISP, ASN, coordinates

```python
# IP geolocation
geo = osint.ipapi_lookup("8.8.8.8")
# Returns: {country, city, lat, lon, isp, as, asname}
```

#### **ASN Information (Team Cymru)**
- **FREE**: Unlimited
- **Features**: ASN, prefix, country, registry

```python
# ASN lookup
asn_data = osint.cymru_asn_lookup("8.8.8.8")
# Returns: {asn, prefix, country, registry, allocated}
```

#### **GitHub Code Search**
- **FREE**: 5,000 requests/hour (with token), 60/hour (without)
- **Features**: Search code, repositories for exposed secrets

```python
# GitHub search
results = osint.github_search("example.com password", in_code=True)
# Returns: List of code files matching query
```

#### **Wayback Machine (Internet Archive)**
- **FREE**: Unlimited
- **Features**: Historical URLs from archives

```python
# Wayback URLs
urls = osint.wayback_urls("example.com")
# Returns: List of archived URLs
```

#### **Have I Been Pwned**
- **FREE**: Unlimited (rate limited)
- **Features**: Check email in data breaches

```python
# Check breaches
breaches = osint.hibp_check_breach("test@example.com")
# Returns: List of breaches with dates, data types
```

#### **SEC EDGAR (Government)**
- **FREE**: Unlimited
- **Features**: Company filings, subsidiaries, officers

```python
# SEC search
filings = osint.sec_edgar_search("Tesla Inc")
# Returns: List of SEC filings
```

#### **Shodan** (optional paid/free tier)
- **FREE**: 100 queries/month
- **PAID**: $59/month (unlimited)
- **Features**: Internet-wide device search

```python
# Shodan search (requires API key)
results = osint.shodan_search("hostname:example.com")
# Returns: List of exposed services
```

---

### **3. Comprehensive OSINT Report**

Run everything at once:

```python
# Complete OSINT collection
report = osint.comprehensive_osint("example.com")

# Report includes:
# - Certificate transparency data
# - DNS records (A, AAAA, MX, NS, TXT)
# - WHOIS information
# - Subdomains from certs
# - IP geolocation
# - ASN information
# - Archived URLs (Wayback Machine)
# - GitHub code exposure
```

---

## Government & Public Data Sources

### **United States**

#### **1. SEC EDGAR** (FREE)
**Purpose**: Company filings, subsidiaries, executive info
**API**: https://www.sec.gov/edgar/sec-api-documentation

**Use Cases**:
- Find company domains from filings
- Identify subsidiaries
- Discover officers/executives
- Track acquisitions

#### **2. USPTO Patents** (FREE)
**Purpose**: Patent search, trademark search
**Access**: https://www.uspto.gov/patents/search

**Use Cases**:
- Technology stack insights
- Innovation areas
- Contact information

#### **3. FCC License View** (FREE)
**Purpose**: Radio/telecom licenses
**Access**: https://wireless2.fcc.gov/UlsApp/UlsSearch/searchLicense.jsp

#### **4. GSA SAM.gov** (FREE)
**Purpose**: Government contractor information
**API**: https://sam.gov/data-services/

#### **5. US Copyright Office** (FREE)
**Purpose**: Copyright registrations
**Access**: https://www.copyright.gov/records/

---

### **International**

#### **RIPE NCC** (Europe) - FREE
**Purpose**: IP allocations, ASN info
**API**: https://stat.ripe.net/docs/data_api

#### **ARIN** (North America) - FREE
**Purpose**: WHOIS, IP allocations
**API**: https://www.arin.net/resources/registry/whois/rws/api/

#### **Companies House** (UK) - FREE
**Purpose**: UK company information
**API**: https://developer.company-information.service.gov.uk/

---

## Unified OSINT Aggregator

**File**: `core/managers/osint_aggregator.py`

### Complete Workflow

```python
from core.managers.osint_aggregator import OSINTAggregator

# Initialize
osint = OSINTAggregator(output_dir="/tmp/osint")

# 1. Comprehensive Reconnaissance
report = osint.comprehensive_recon("example.com")

# The aggregator runs:
# - Google Dorking (100 categories)
# - Certificate Transparency (crt.sh)
# - DNS/WHOIS lookups
# - Subdomain enumeration (Amass)
# - HTTP probing (httpx)
# - URL discovery (Wayback, GAU)
# - GitHub code search
# - IP geolocation & ASN

# 2. Search for Credentials (use ethically!)
cred_exposure = osint.search_credentials("example.com")

# 3. Company Intelligence
company_intel = osint.search_company_intel("Tesla Inc")

# 4. Export Report
json_report = osint.export_report(report, format="json")
md_report = osint.export_report(report, format="markdown")

# 5. Check Tool Status
status = osint.get_status()
print(status)
# {"google_dorks": True, "osint_apis": True, "amass": True, ...}
```

---

## Workflow Phases

### **Phase 1: Google Dorking**
- Runs pre-built dork queries
- Discovers exposed files, admin panels, errors
- Finds login pages, API endpoints
- Detects credential exposure

### **Phase 2: Free OSINT APIs**
- Certificate transparency (subdomains)
- DNS/WHOIS lookups
- IP geolocation & ASN
- GitHub code search
- Wayback Machine URLs

### **Phase 3: Subdomain Enumeration**
- Amass comprehensive mode
- Combines passive & active discovery
- DNS resolution & verification

### **Phase 4: HTTP Probing**
- Probe live hosts with httpx
- Extract titles, status codes
- Technology fingerprinting
- Screenshot capture (optional)

### **Phase 5: URL Discovery**
- Wayback Machine archives
- GAU (GetAllUrls)
- URL categorization (APIs, params, files)

---

## API Configuration

### **Minimal (FREE)**

```bash
# Only required for enhanced features
GOOGLE_API_KEY=your_google_api_key  # 100 queries/day FREE
GOOGLE_CSE_ID=your_cse_id
GITHUB_TOKEN=ghp_your_token  # FREE - 5,000 req/hour
```

### **Enhanced (FREE TIERS)**

```bash
# All have generous free tiers
VIRUSTOTAL_API_KEY=your_key  # 4 req/min FREE
SHODAN_API_KEY=your_key  # 100 queries/month FREE
CENSYS_API_ID=your_id  # 250 queries/month FREE
CENSYS_SECRET=your_secret
IPINFO_TOKEN=your_token  # 50,000 req/month FREE
```

### **No API Key Required**

These work without any configuration:
- crt.sh (certificate transparency)
- DNS lookups (command-line)
- WHOIS lookups (command-line)
- ip-api.com (45 req/min)
- Team Cymru ASN
- Wayback Machine
- Have I Been Pwned
- SEC EDGAR

---

## Example Outputs

### Subdomain Discovery

```
Found 237 unique subdomains:
- www.example.com
- api.example.com
- admin.example.com
- staging.example.com
- dev.example.com
...
```

### Live Host Probing

```
Found 42 live hosts:
- https://example.com [200] "Example Domain" [Nginx, CloudFlare]
- https://api.example.com [200] "API Gateway" [Express.js]
- https://admin.example.com [403] "Forbidden"
...
```

### Google Dorks Results

```
Exposed Files:
- https://example.com/docs/internal-report.pdf
- https://example.com/backup.sql
- https://example.com/.env

Admin Panels:
- https://admin.example.com/login
- https://example.com/cpanel
- https://example.com/administrator

GitHub Exposure:
- example/repo1 - config.js contains API keys
- example/repo2 - database.yml contains credentials
```

---

## Best Practices

### **OPSEC Guidelines**

1. **Rate Limiting**
   - Google: Max 100 queries/day (free tier)
   - VirusTotal: 4 req/min
   - ip-api: 45 req/min
   - Respect all rate limits

2. **Ethical Use**
   - Only scan authorized targets
   - Don't abuse free APIs
   - Respect robots.txt
   - Follow bug bounty program rules

3. **Data Privacy**
   - Don't store sensitive data unnecessarily
   - Secure all OSINT reports
   - Delete after use
   - Never share credential exposures publicly

### **Optimization Tips**

1. **Free Tier Strategy**
   - Use crt.sh first (unlimited, fast)
   - DNS lookups are free (use extensively)
   - Save Google Dorks for specific queries
   - Use Shodan sparingly (100/month limit)

2. **Deduplication**
   - Combine results from multiple sources
   - Deduplicate subdomains
   - Prioritize high-confidence findings

3. **Automation**
   - Run OSINT during off-peak hours
   - Cache results to avoid re-querying
   - Use async operations where possible

---

## Integration with Bug Bounty Workflow

```python
from core.managers.bugbounty_toolkit_manager import BugBountyToolkitManager
from core.managers.osint_aggregator import OSINTAggregator

# Initialize both
bug_bounty = BugBountyToolkitManager(opsec_level="medium")
osint = OSINTAggregator()

# Step 1: OSINT Reconnaissance
osint_report = osint.comprehensive_recon("example.com")

# Step 2: Use OSINT data for bug bounty hunting
recon_data = {
    "subdomains": osint_report["subdomains"],
    "live_hosts": osint_report["live_hosts"],
    "urls": osint_report["urls"]
}

# Step 3: Run vulnerability scanning
findings = bug_bounty.vulnerability_scanning(recon_data)

# Step 4: Validate and report
for finding in findings:
    if finding.get("confidence", 0) >= 0.7:
        # Create TheHive case
        # Enrich with Cortex
        # Trigger Shuffle playbook
        pass
```

---

## Summary

### **New Capabilities**

✅ **Google Dorking**: 10 pre-built categories, automated searching
✅ **Certificate Transparency**: Subdomain discovery via crt.sh
✅ **DNS/WHOIS**: Complete DNS enumeration, WHOIS data
✅ **IP Intelligence**: Geolocation, ASN, ISP information
✅ **GitHub Search**: Find exposed secrets in code
✅ **Wayback Machine**: Historical URL discovery
✅ **Breach Database**: Check emails in breaches
✅ **Government Data**: SEC filings, USPTO patents
✅ **Unified Aggregator**: Single interface for all sources

### **Files Created**

- `core/tools/google_dorks_wrapper.py` (290 lines)
- `core/tools/osint_apis_wrapper.py` (450 lines)
- `core/managers/osint_aggregator.py` (380 lines)
- `API_KEYS_GUIDE.md` (500 lines)
- `OSINT_GUIDE.md` (this file, 550 lines)

**Total**: ~2,170 lines of OSINT code + documentation

### **Cost**

**Completely FREE**: $0/month (using only free APIs)
**Enhanced**: $0-5/month (with Google API optional)
**All tools use free tiers or no API keys required!**

🎯 **World-class OSINT reconnaissance with ZERO cost!**
