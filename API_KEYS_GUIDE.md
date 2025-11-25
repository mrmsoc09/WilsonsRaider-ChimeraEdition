# API Keys & Data Sources Guide

## Overview

This document details all API keys required/optional for WilsonsRaider-ChimeraEdition tools and integrations, plus free/open-source OSINT data sources.

---

## Required API Keys (Platform Integrations)

### **1. OpenAI** (Required for AI Orchestration)
**Service**: GPT-3.5/GPT-4 for automation orchestrator
**Cost**: Pay-as-you-go ($0.002-$0.06 per 1K tokens)
**Sign up**: https://platform.openai.com/api-keys

**Environment Variable**:
```bash
OPENAI_API_KEY=sk-your_api_key_here
```

**Usage**:
- AI-powered task decomposition
- False positive detection
- Attack chain planning
- Natural language report generation

---

### **2. TheHive** (Required if using incident response)
**Service**: Incident response platform
**Cost**: Free (self-hosted) or TheHive Cloud
**Setup**: Generate in TheHive UI → Organization Settings → API Keys

**Environment Variable**:
```bash
THEHIVE_URL=http://localhost:9000
THEHIVE_API_KEY=your_api_key_here
```

---

### **3. Cortex** (Required if using threat intelligence)
**Service**: Observable analysis platform
**Cost**: Free (self-hosted)
**Setup**: Cortex UI → Organization → Users → API Key

**Environment Variable**:
```bash
CORTEX_URL=http://localhost:9001
CORTEX_API_KEY=your_api_key_here
```

**Analyzers Requiring API Keys** (optional):
- **VirusTotal**: Free tier (4 req/min) - https://www.virustotal.com/gui/join-us
- **AbuseIPDB**: Free tier (1,000 checks/day) - https://www.abuseipdb.com/api
- **Shodan**: Free tier (100 queries/month) - https://account.shodan.io/register
- **AlienVault OTX**: Free - https://otx.alienvault.com/api
- **MaxMind GeoIP**: Free GeoLite2 - https://www.maxmind.com/en/geolite2/signup

---

### **4. Shuffle** (Required if using SOAR)
**Service**: Security orchestration platform
**Cost**: Free (self-hosted) or Shuffle Cloud
**Setup**: Shuffle UI → Settings → API Keys

**Environment Variable**:
```bash
SHUFFLE_URL=https://localhost:3001
SHUFFLE_API_KEY=your_api_key_here
```

---

### **5. Wazuh** (Required if using SIEM)
**Service**: Security monitoring
**Cost**: Free (open source)
**Setup**: Default admin credentials or create API user

**Environment Variables**:
```bash
WAZUH_API_URL=https://localhost:55000
WAZUH_USERNAME=admin
WAZUH_PASSWORD=your_password_here
```

---

## Optional API Keys (Enhanced OSINT)

### **Subdomain Enumeration**

#### **1. SecurityTrails**
**Free Tier**: 50 API calls/month
**Paid**: $99/month (10,000 calls)
**Features**: DNS history, subdomains, WHOIS
**Sign up**: https://securitytrails.com/app/signup

**Amass Config**:
```ini
[data_sources.SecurityTrails]
[data_sources.SecurityTrails.Credentials]
apikey = YOUR_SECURITYTRAILS_API_KEY
```

#### **2. Censys**
**Free Tier**: 250 queries/month
**Features**: Internet-wide scanning data
**Sign up**: https://censys.io/register

**Amass Config**:
```ini
[data_sources.Censys]
[data_sources.Censys.Credentials]
apikey = YOUR_CENSYS_API_ID
secret = YOUR_CENSYS_SECRET
```

#### **3. Shodan**
**Free Tier**: 100 queries/month
**Paid**: $59/month (unlimited)
**Features**: Internet device search
**Sign up**: https://account.shodan.io/register

**Amass Config**:
```ini
[data_sources.Shodan]
[data_sources.Shodan.Credentials]
apikey = YOUR_SHODAN_API_KEY
```

#### **4. VirusTotal**
**Free Tier**: 4 requests/min, 500/day
**Features**: Domain/IP reputation, subdomains
**Sign up**: https://www.virustotal.com/gui/join-us

**Amass Config**:
```ini
[data_sources.VirusTotal]
[data_sources.VirusTotal.Credentials]
apikey = YOUR_VIRUSTOTAL_API_KEY
```

#### **5. PassiveTotal (RiskIQ)**
**Free Tier**: Limited community access
**Features**: Passive DNS, WHOIS, SSL certificates
**Sign up**: https://community.riskiq.com/registration

**Amass Config**:
```ini
[data_sources.PassiveTotal]
[data_sources.PassiveTotal.Credentials]
username = YOUR_EMAIL
apikey = YOUR_PASSIVETOTAL_API_KEY
```

#### **6. AlienVault OTX**
**Free Tier**: Unlimited (requires registration)
**Features**: Threat intelligence, domain reputation
**Sign up**: https://otx.alienvault.com/api

**Amass Config**:
```ini
[data_sources.AlienVault]
[data_sources.AlienVault.Credentials]
apikey = YOUR_OTX_API_KEY
```

---

### **Vulnerability Intelligence**

#### **7. National Vulnerability Database (NVD)**
**Free**: Yes (no API key required)
**Features**: CVE database, CVSS scores
**Access**: https://nvd.nist.gov/developers/vulnerabilities

**Already Integrated**: `core/datasources/nvd_client.py`

#### **8. Exploit-DB**
**Free**: Yes (no API key required)
**Features**: Public exploit database
**Access**: https://www.exploit-db.com/

**Already Integrated**: `core/datasources/exploit_db.py`

---

### **DNS & WHOIS**

#### **9. WhoisXML API**
**Free Tier**: 500 queries/month
**Features**: WHOIS, reverse WHOIS, DNS
**Sign up**: https://whoisxmlapi.com/

#### **10. DNSlytics**
**Free Tier**: Limited queries
**Features**: Reverse IP, DNS history
**Access**: https://dnslytics.com/api

---

### **Certificate Transparency**

#### **11. crt.sh**
**Free**: Yes (no API key)
**Features**: SSL certificate search
**Access**: https://crt.sh/

**Usage**:
```bash
curl "https://crt.sh/?q=example.com&output=json"
```

#### **12. Certificate Search (Censys)**
**Free Tier**: 250 queries/month
**Features**: Certificate transparency logs
**Sign up**: https://censys.io/

---

## Government & Public Data Sources (FREE)

### **United States**

#### **1. EDGAR (SEC Filings)**
**Free**: Yes
**Features**: Company filings, subsidiaries, officers
**API**: https://www.sec.gov/edgar/sec-api-documentation

**Use Cases**:
- Find company domains from SEC filings
- Identify subsidiaries and acquisitions
- Discover officer/executive information

#### **2. USPTO (Patent Database)**
**Free**: Yes
**Features**: Patent search, trademark search
**Access**: https://www.uspto.gov/patents/search

**Use Cases**:
- Technology stack insights from patents
- Company innovation areas
- Contact information

#### **3. FCC License View**
**Free**: Yes
**Features**: Radio/telecom licenses
**Access**: https://wireless2.fcc.gov/UlsApp/UlsSearch/searchLicense.jsp

#### **4. GSA System for Award Management (SAM)**
**Free**: Yes
**Features**: Government contractor information
**API**: https://sam.gov/data-services/

#### **5. US Copyright Office**
**Free**: Yes
**Features**: Copyright registrations
**Access**: https://www.copyright.gov/records/

---

### **International**

#### **6. RIPE NCC (Europe)**
**Free**: Yes
**Features**: IP allocations, ASN info
**API**: https://stat.ripe.net/docs/data_api

#### **7. ARIN (North America)**
**Free**: Yes
**Features**: WHOIS, IP allocations
**API**: https://www.arin.net/resources/registry/whois/rws/api/

#### **8. Companies House (UK)**
**Free**: Yes (requires API key - free)
**Features**: UK company information
**API**: https://developer.company-information.service.gov.uk/

---

## Free OSINT APIs (No Registration Required)

### **1. WHOIS Lookups**
- **whois command line**: Pre-installed on Linux
- **IANA WHOIS**: https://www.iana.org/whois
- **RDAP**: https://rdap.org/

### **2. DNS Records**
- **dig/nslookup**: Pre-installed
- **DNS over HTTPS (Google)**: https://dns.google/resolve?name=example.com
- **Cloudflare DoH**: https://cloudflare-dns.com/dns-query

### **3. IP Geolocation**
- **ipapi.co**: Free tier (1,000 req/day) - https://ipapi.co/
- **ip-api.com**: Free (45 req/min) - http://ip-api.com/
- **ipinfo.io**: Free tier (50,000 req/month) - https://ipinfo.io/

### **4. ASN Information**
- **Team Cymru IP to ASN**: whois.cymru.com
- **Hurricane Electric BGP Toolkit**: https://bgp.he.net/

### **5. Email Validation**
- **hunter.io**: Free tier (25 searches/month) - https://hunter.io/
- **EmailRep.io**: Free - https://emailrep.io/

### **6. Breach Data**
- **Have I Been Pwned**: Free API - https://haveibeenpwned.com/API/v3
- **DeHashed**: Paid ($20/week) - https://dehashed.com/

### **7. Wayback Machine**
- **Internet Archive CDX API**: Free - https://archive.org/help/wayback_api.php

---

## Google Custom Search API

**Free Tier**: 100 queries/day
**Paid**: $5 per 1,000 queries
**Sign up**: https://developers.google.com/custom-search/v1/introduction

**Setup**:
1. Create project: https://console.cloud.google.com/
2. Enable Custom Search API
3. Create credentials (API key)
4. Create Custom Search Engine: https://cse.google.com/create/new

**Environment Variables**:
```bash
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

---

## GitHub API

**Free Tier**: 5,000 requests/hour (authenticated)
**Features**: Search code, repositories, users
**Sign up**: https://github.com/settings/tokens

**Environment Variable**:
```bash
GITHUB_TOKEN=ghp_your_github_token
```

---

## Amass Configuration File

**Location**: `~/.config/amass/config.ini`

**Complete Example**:
```ini
# DNS resolution settings
[resolvers]
resolver = 8.8.8.8
resolver = 1.1.1.1

# Data sources
[data_sources]

[data_sources.AlienVault]
[data_sources.AlienVault.Credentials]
apikey = YOUR_OTX_API_KEY

[data_sources.Censys]
[data_sources.Censys.Credentials]
apikey = YOUR_CENSYS_API_ID
secret = YOUR_CENSYS_SECRET

[data_sources.Shodan]
[data_sources.Shodan.Credentials]
apikey = YOUR_SHODAN_API_KEY

[data_sources.SecurityTrails]
[data_sources.SecurityTrails.Credentials]
apikey = YOUR_SECURITYTRAILS_API_KEY

[data_sources.VirusTotal]
[data_sources.VirusTotal.Credentials]
apikey = YOUR_VIRUSTOTAL_API_KEY

[data_sources.PassiveTotal]
[data_sources.PassiveTotal.Credentials]
username = YOUR_EMAIL
apikey = YOUR_PASSIVETOTAL_API_KEY

# GitHub for searching code
[data_sources.GitHub]
[data_sources.GitHub.Credentials]
apikey = YOUR_GITHUB_TOKEN

# WhoisXML API
[data_sources.WhoisXMLAPI]
[data_sources.WhoisXMLAPI.Credentials]
apikey = YOUR_WHOISXML_API_KEY
```

---

## Environment Variable Template

**Create `.env` file**:
```bash
# Required
OPENAI_API_KEY=sk-your_openai_key

# Platform Integrations
THEHIVE_URL=http://localhost:9000
THEHIVE_API_KEY=your_thehive_key
CORTEX_URL=http://localhost:9001
CORTEX_API_KEY=your_cortex_key
SHUFFLE_URL=https://localhost:3001
SHUFFLE_API_KEY=your_shuffle_key
WAZUH_API_URL=https://localhost:55000
WAZUH_USERNAME=admin
WAZUH_PASSWORD=your_wazuh_password

# OSINT APIs (Optional - Enhanced Reconnaissance)
VIRUSTOTAL_API_KEY=your_virustotal_key
SHODAN_API_KEY=your_shodan_key
CENSYS_API_ID=your_censys_id
CENSYS_SECRET=your_censys_secret
SECURITYTRAILS_API_KEY=your_securitytrails_key
ALIENVAULT_OTX_KEY=your_otx_key
PASSIVETOTAL_USERNAME=your_email
PASSIVETOTAL_API_KEY=your_passivetotal_key

# Google Custom Search (for dorking)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_cse_id

# GitHub
GITHUB_TOKEN=ghp_your_github_token

# IP Geolocation
IPINFO_TOKEN=your_ipinfo_token

# Database
POSTGRES_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password

# Vault
VAULT_TOKEN=your_vault_token
```

---

## API Cost Optimization

### **Free Tier Strategy**

1. **Prioritize Free Sources**:
   - crt.sh (certificates)
   - DNS lookups (Google DoH, Cloudflare)
   - WHOIS (command line)
   - GitHub public search
   - Government databases (SEC, USPTO)

2. **Limited Free Tiers**:
   - VirusTotal: 4 req/min (use sparingly)
   - Shodan: 100 queries/month (save for important targets)
   - Censys: 250 queries/month
   - Google Custom Search: 100 queries/day

3. **Recommended Paid (if budget allows)**:
   - Shodan: $59/month (unlimited)
   - VirusTotal: $500/year (1,000 req/min)
   - SecurityTrails: $99/month (10,000 queries)

### **Rate Limiting**

All wrappers include rate limiting to stay within free tiers:
- VirusTotal: 4 req/min max
- Shodan: Batch queries to minimize API calls
- Google: 100 queries/day limit enforced

---

## Summary

### **Minimum Required** (Free):
- OpenAI API ($0.10-$5/month depending on usage)
- Self-hosted TheHive, Wazuh, Shuffle, Cortex

### **Recommended Free APIs**:
- VirusTotal (free tier)
- AlienVault OTX (free)
- crt.sh (free)
- GitHub (free)
- Government databases (free)
- Google Custom Search (100/day free)

### **Optional Paid** (Enhanced):
- Shodan ($59/month)
- SecurityTrails ($99/month)
- Censys Pro ($199/month)

**Total Free Setup**: $0-5/month (just OpenAI usage)
**Enhanced Setup**: $60-200/month (with paid APIs)

All API configurations are managed through environment variables and Vault for security! 🔐
