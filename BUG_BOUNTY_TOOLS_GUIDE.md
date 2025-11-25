# Bug Bounty Tools Integration Guide

## Overview

WilsonsRaider-ChimeraEdition now includes **production-grade integrations** for industry-standard bug bounty hunting tools, fully orchestrated with AI-powered workflows and security platform integrations.

---

## Integrated Bug Bounty Tools

### **Reconnaissance Tools**

#### 1. **Amass** (`core/tools/amass_wrapper.py`)
**Purpose**: Advanced subdomain enumeration with OSINT and active DNS resolution

**Capabilities**:
- Passive subdomain enumeration (OSINT sources)
- Active subdomain enumeration with DNS resolution
- Organization intelligence gathering
- Comprehensive mode (passive + active)
- Network graph visualization

**Usage**:
```python
from core.tools.amass_wrapper import AmassWrapper

amass = AmassWrapper()

# Passive enumeration (stealthy)
results = amass.enum_passive("example.com")
# Returns: {"subdomains": [...], "count": 150}

# Active enumeration (with DNS resolution)
results = amass.enum_active("example.com", brute_force=True)

# Comprehensive (recommended)
results = amass.enum_comprehensive("example.com")

# Organization intel
results = amass.intel("Example Corp", whois=True)
```

**OPSEC Considerations**:
- Passive mode: Stealthy, no direct target contact
- Active mode: Generates DNS queries (detectable)
- Rate limiting: Configurable (default: 10 req/s)

---

#### 2. **Subfinder** (`core/tools/subfinder_wrapper.py`)
**Purpose**: Fast passive subdomain discovery

**Capabilities**:
- Passive subdomain enumeration
- Multiple OSINT sources
- Silent mode for clean output

**Usage**:
```python
from core.tools.subfinder_wrapper import SubfinderWrapper

subfinder = SubfinderWrapper("example.com")
subdomains = subfinder.run()
# Returns: ["sub1.example.com", "sub2.example.com", ...]
```

---

#### 3. **httpx** (`core/tools/httpx_wrapper.py`)
**Purpose**: HTTP probing for live host detection and metadata extraction

**Capabilities**:
- HTTP/HTTPS probing
- Title extraction
- Status code detection
- Technology fingerprinting
- Screenshot capture
- Server header extraction

**Usage**:
```python
from core.tools.httpx_wrapper import HttpxWrapper

httpx = HttpxWrapper()

urls = ["https://example.com", "https://api.example.com"]
results = httpx.probe_urls(
    urls,
    tech_detect=True,
    screenshot=True,
    follow_redirects=True
)

# Returns live hosts with metadata
for host in results["live_hosts"]:
    print(f"{host['url']} - {host['title']} - {host['technologies']}")
```

---

#### 4. **Waybackurls / GAU** (`core/tools/waybackurls_wrapper.py`)
**Purpose**: URL discovery from web archives

**Capabilities**:
- Fetch URLs from Wayback Machine
- Fetch URLs from multiple archives (via GAU)
- Automatic categorization (API endpoints, parameters, files)

**Usage**:
```python
from core.tools.waybackurls_wrapper import ArchiveURLWrapper

archive = ArchiveURLWrapper()

results = archive.fetch_urls("example.com", include_subs=True)

# Access categorized URLs
api_endpoints = results["categorized"]["api_endpoints"]
param_urls = results["categorized"]["with_parameters"]
js_files = results["categorized"]["files"]["js"]
```

---

### **Vulnerability Scanning Tools**

#### 5. **Nuclei** (`core/tools/nuclei_wrapper.py`)
**Purpose**: Template-based vulnerability scanning

**Capabilities**:
- 7,000+ community templates
- CVE detection
- Misconfigurations
- Exposed panels
- Technology-specific checks

**Usage**:
```python
from core.tools.nuclei_wrapper import NucleiWrapper

nuclei = NucleiWrapper("https://example.com")
results = nuclei.run()
```

**Note**: Enhanced version recommended (see below for improvements)

---

#### 6. **ffuf** (`core/tools/ffuf_wrapper.py`)
**Purpose**: Web fuzzing for directory/file/parameter discovery

**Capabilities**:
- Directory & file fuzzing
- Parameter fuzzing (GET/POST)
- Virtual host discovery
- API endpoint fuzzing
- Recursive fuzzing
- Auto-calibration for false positives

**Usage**:
```python
from core.tools.ffuf_wrapper import FfufWrapper

ffuf = FfufWrapper()

# Directory fuzzing
results = ffuf.fuzz_directories(
    url="https://example.com/FUZZ",
    extensions=['.php', '.html', '.asp'],
    recursion=True,
    recursion_depth=2
)

# Parameter fuzzing
results = ffuf.fuzz_parameters(
    url="https://example.com/api?FUZZ=value",
    method="GET"
)

# Virtual host discovery
results = ffuf.fuzz_vhosts(url="https://example.com")

# API fuzzing
results = ffuf.api_fuzz(
    base_url="https://api.example.com",
    endpoints=["/users", "/posts", "/admin"],
    methods=["GET", "POST", "PUT", "DELETE"]
)
```

**Key Features**:
- Rate limiting (100 req/s default)
- Auto-calibration filters false positives
- JSON output parsing
- Match/filter by status code, size, words

---

#### 7. **SQLMap** (`core/tools/sqlmap_wrapper.py`)
**Purpose**: Automated SQL injection detection and exploitation

**Capabilities**:
- SQL injection testing (Boolean, Error, Union, Stacked, Time-based)
- Database enumeration
- Table enumeration
- Data extraction
- OS shell access (highly intrusive)
- WAF detection

**Usage**:
```python
from core.tools.sqlmap_wrapper import SQLMapWrapper

sqlmap = SQLMapWrapper(risk_level=1)

# Test for SQL injection
results = sqlmap.test_injection(
    url="https://example.com/product?id=1",
    batch=True  # Automated mode
)

if results["vulnerable"]:
    # Enumerate databases
    dbs = sqlmap.enumerate_databases(url)

    # Enumerate tables
    tables = sqlmap.enumerate_tables(url, database="app_db")

    # Dump data (limit 100 rows)
    data = sqlmap.dump_table(
        url,
        database="app_db",
        table="users",
        columns=["username", "email"],
        limit_rows=100
    )
```

**OPSEC WARNING**:
- Risk levels: 1 (safe), 2 (medium), 3 (intrusive)
- OS shell access is **highly intrusive** - use only with authorization
- Always use `--batch` mode for automation

---

## Unified Bug Bounty Toolkit Manager

**File**: `core/managers/bugbounty_toolkit_manager.py`

### Complete Automated Workflow

The `BugBountyToolkitManager` orchestrates all tools in an intelligent, sequential workflow:

```
Phase 1: Reconnaissance
  ├─ Amass (subdomain enumeration)
  ├─ Httpx (live host probing)
  └─ Waybackurls (URL discovery)

Phase 2: Vulnerability Scanning
  ├─ Nuclei (template scanning)
  ├─ ffuf (directory/parameter fuzzing)
  └─ SQLMap (SQL injection testing)

Phase 3: Validation & Enrichment
  ├─ ValidationManager (confidence scoring)
  ├─ Cortex (threat intelligence)
  └─ TheHive (case creation for HIGH/CRITICAL)

Phase 4: Incident Response
  ├─ Shuffle (trigger playbooks)
  └─ Wazuh (SIEM logging)

Phase 5: Reporting
  └─ Generate comprehensive markdown/HTML report
```

### Usage Example

```python
from core.managers.bugbounty_toolkit_manager import BugBountyToolkitManager

# Initialize toolkit with medium OPSEC
toolkit = BugBountyToolkitManager(
    output_dir="/tmp/bugbounty",
    opsec_level="medium",  # low/medium/high
    enable_integrations=True
)

# Run full workflow
results = toolkit.run_full_workflow(
    target_domain="example.com",
    program_name="HackerOne_Example"
)

print(f"Found {results['findings_count']} validated vulnerabilities")
print(f"Created {len(results['cases_created'])} TheHive cases")
print(f"Report: {results['report_path']}")
```

### OPSEC Levels

| Level  | Rate Limit | Threads | Aggressive | Use Case                |
|--------|------------|---------|------------|-------------------------|
| Low    | 150 req/s  | 100     | Yes        | Local testing           |
| Medium | 100 req/s  | 50      | No         | **Recommended default** |
| High   | 50 req/s   | 25      | No         | Stealth operations      |

---

## Tool Availability Check

```python
# Check which tools are installed
toolkit = BugBountyToolkitManager()
status = toolkit.get_toolkit_status()

print("Tools:", status["tools"])
# {"amass": True, "httpx": True, "ffuf": True, "sqlmap": True}

print("Integrations:", status["integrations"])
# {"thehive": True, "wazuh": True, "shuffle": True, "cortex": True}
```

---

## Installation Requirements

### Tool Installation

```bash
# Amass
wget https://github.com/OWASP/Amass/releases/latest/download/amass_Linux_amd64.zip
unzip amass_Linux_amd64.zip
sudo mv amass /usr/local/bin/

# Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Nuclei
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
nuclei -update-templates

# ffuf
go install github.com/ffuf/ffuf@latest

# SQLMap
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap
ln -s /opt/sqlmap/sqlmap.py /usr/local/bin/sqlmap

# Waybackurls
go install github.com/tomnomnom/waybackurls@latest

# GAU (GetAllUrls)
go install github.com/lc/gau/v2/cmd/gau@latest

# Wordlists
sudo apt install seclists
# Or manually:
git clone https://github.com/danielmiessler/SecLists.git /usr/share/wordlists/SecLists
```

### Docker Installation

All tools are pre-installed in the enhanced Docker image:

```bash
docker build -t wilsons-raider:latest -f Dockerfile.enhanced .
```

---

## API Integration Examples

### Complete Bug Bounty Workflow via Dashboard API

```bash
# Start a scan
curl -X POST http://localhost:8000/api/bugbounty/scan \
  -H "Content-Type: application/json" \
  -d '{
    "target": "example.com",
    "program": "HackerOne_Example",
    "opsec_level": "medium"
  }'

# Get scan status
curl http://localhost:8000/api/bugbounty/scan/{scan_id}/status

# Get findings
curl http://localhost:8000/api/bugbounty/scan/{scan_id}/findings
```

---

## Advanced Usage

### Custom Reconnaissance Workflow

```python
from core.managers.bugbounty_toolkit_manager import BugBountyToolkitManager

toolkit = BugBountyToolkitManager()

# Run only reconnaissance
recon_results = toolkit.reconnaissance("example.com")

# Access results
subdomains = recon_results["subdomains"]
live_hosts = recon_results["live_hosts"]
urls = recon_results["urls"]
technologies = recon_results["technologies"]

print(f"Found {len(subdomains)} subdomains")
print(f"Technologies: {', '.join(technologies)}")
```

### Custom Vulnerability Scanning

```python
# Prepare recon data
recon_data = {
    "live_hosts": [
        {"url": "https://example.com", "status_code": 200},
        {"url": "https://api.example.com", "status_code": 200}
    ],
    "urls": ["https://example.com/product?id=1"]
}

# Run vulnerability scanning
findings = toolkit.vulnerability_scanning(recon_data)

for finding in findings:
    print(f"{finding['severity']}: {finding['name']} on {finding['target']}")
```

---

## Tool-Specific Advanced Features

### Amass Configuration File

Create `~/.config/amass/config.ini`:

```ini
[data_sources]
[data_sources.VirusTotal]
[data_sources.VirusTotal.Credentials]
apikey = YOUR_VIRUSTOTAL_API_KEY

[data_sources.Shodan]
[data_sources.Shodan.Credentials]
apikey = YOUR_SHODAN_API_KEY

[data_sources.Censys]
[data_sources.Censys.Credentials]
apikey = YOUR_CENSYS_API_ID
secret = YOUR_CENSYS_SECRET
```

### ffuf Custom Wordlists

```python
ffuf = FfufWrapper()

# Use custom wordlist
results = ffuf.fuzz_directories(
    url="https://example.com/FUZZ",
    wordlist="/custom/wordlists/directories.txt"
)
```

### SQLMap Session Management

```python
sqlmap = SQLMapWrapper()

# Test injection (creates session)
results = sqlmap.test_injection(url)

# Resume from session for enumeration
if results["vulnerable"]:
    # Session file is automatically reused
    dbs = sqlmap.enumerate_databases(url)
```

---

## Best Practices

### 1. OPSEC Guidelines
- Always use `opsec_level="high"` for production bug bounty programs
- Respect rate limits (check program rules)
- Use random User-Agent rotation
- Space out requests with jitter
- Avoid aggressive scanning on production systems

### 2. Scope Validation
- **Always** verify target is in scope before scanning
- Check program rules for forbidden paths/endpoints
- Use `--exclude` flags for out-of-scope subdomains

### 3. Result Validation
- All findings require manual verification
- False positives are common - validate before reporting
- Use confidence scores: Only report ≥ 0.7

### 4. Data Handling
- Never dump sensitive production data
- Use `limit_rows` with SQLMap dumps
- Secure storage for all results
- Delete findings after reporting

### 5. Responsible Disclosure
- Report all findings through proper channels
- Do **not** exploit beyond PoC
- No DoS attacks or service disruption
- Respect program timelines

---

## Troubleshooting

### Tool Not Found

```python
# Check if tool is installed
import subprocess
try:
    subprocess.run(['amass', '-version'], check=True)
    print("Amass is installed")
except FileNotFoundError:
    print("Amass not found - install it")
```

### Rate Limiting Errors

```python
# Reduce rate limit
toolkit = BugBountyToolkitManager(opsec_level="high")

# Or manually
ffuf = FfufWrapper(rate_limit=50)  # Down from 100
```

### Timeout Issues

```python
# Increase timeouts
sqlmap = SQLMapWrapper()
results = sqlmap.test_injection(url, timeout=3600)  # 1 hour
```

---

## Summary

**New Bug Bounty Tools Added**:
- ✅ Amass (subdomain enumeration)
- ✅ httpx (HTTP probing)
- ✅ Waybackurls/GAU (URL discovery)
- ✅ ffuf (web fuzzing)
- ✅ SQLMap (SQL injection)

**Total Tool Wrappers**: 20+ production-grade integrations

**Unified Orchestration**: `BugBountyToolkitManager` for complete automated workflows

**Integration**: Full integration with TheHive, Wazuh, Shuffle, and Cortex

All tools are production-ready with proper error handling, rate limiting, OPSEC controls, and output parsing! 🎯
