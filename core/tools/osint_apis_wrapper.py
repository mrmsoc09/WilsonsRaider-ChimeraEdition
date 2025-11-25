"""Free OSINT APIs Wrapper - Government & Public Data Sources

Comprehensive integration of free/open-source OSINT data sources including
government databases, public APIs, and certificate transparency.
Version: 1.0.0
"""

import os
import requests
import logging
import json
import socket
import subprocess
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OSINTAPIsWrapper:
    """Unified wrapper for free OSINT data sources."""

    def __init__(self):
        """Initialize OSINT APIs wrapper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WilsonsRaider-OSINT/1.0'
        })

        # Optional API keys (all have free tiers)
        self.virustotal_key = os.getenv("VIRUSTOTAL_API_KEY")
        self.shodan_key = os.getenv("SHODAN_API_KEY")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.ipinfo_token = os.getenv("IPINFO_TOKEN")

        logger.info("OSINT APIs wrapper initialized")

    # === Certificate Transparency ===

    def crtsh_search(self, domain: str) -> List[Dict[str, Any]]:
        """
        Search crt.sh for SSL certificates (FREE - no API key).

        Args:
            domain: Domain to search

        Returns:
            List of certificates with subdomains
        """
        logger.info(f"Searching crt.sh for {domain}")

        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Extract unique subdomains
            subdomains = set()
            for cert in data:
                name_value = cert.get("name_value", "")
                for name in name_value.split('\n'):
                    name = name.strip().replace('*', '')
                    if name and domain in name:
                        subdomains.add(name)

            logger.info(f"crt.sh found {len(subdomains)} unique subdomains")

            return [
                {
                    "issuer_ca_id": cert.get("issuer_ca_id"),
                    "issuer_name": cert.get("issuer_name"),
                    "common_name": cert.get("common_name"),
                    "name_value": cert.get("name_value"),
                    "entry_timestamp": cert.get("entry_timestamp"),
                    "not_before": cert.get("not_before"),
                    "not_after": cert.get("not_after")
                }
                for cert in data
            ]

        except Exception as e:
            logger.error(f"crt.sh search failed: {e}")
            return []

    # === DNS & WHOIS (FREE) ===

    def dns_lookup(self, domain: str, record_type: str = "A") -> List[str]:
        """
        Perform DNS lookup (FREE - no API key).

        Args:
            domain: Domain to query
            record_type: DNS record type (A, AAAA, MX, NS, TXT, etc.)

        Returns:
            List of DNS records
        """
        logger.info(f"DNS lookup: {domain} ({record_type})")

        try:
            import dns.resolver

            answers = dns.resolver.resolve(domain, record_type)
            records = [str(rdata) for rdata in answers]

            logger.info(f"Found {len(records)} {record_type} records")
            return records

        except ImportError:
            logger.error("dnspython not installed. Install: pip install dnspython")
            return []
        except Exception as e:
            logger.error(f"DNS lookup failed: {e}")
            return []

    def whois_lookup(self, domain: str) -> Dict[str, Any]:
        """
        WHOIS lookup using command-line tool (FREE).

        Args:
            domain: Domain to query

        Returns:
            Parsed WHOIS data
        """
        logger.info(f"WHOIS lookup: {domain}")

        try:
            result = subprocess.run(
                ['whois', domain],
                capture_output=True,
                text=True,
                timeout=30
            )

            whois_text = result.stdout

            # Basic parsing
            data = {
                "raw": whois_text,
                "registrar": None,
                "creation_date": None,
                "expiration_date": None,
                "name_servers": []
            }

            for line in whois_text.split('\n'):
                lower_line = line.lower()

                if 'registrar:' in lower_line:
                    data["registrar"] = line.split(':', 1)[1].strip()
                elif 'creation date:' in lower_line or 'created:' in lower_line:
                    data["creation_date"] = line.split(':', 1)[1].strip()
                elif 'expir' in lower_line and 'date' in lower_line:
                    data["expiration_date"] = line.split(':', 1)[1].strip()
                elif 'name server:' in lower_line:
                    ns = line.split(':', 1)[1].strip()
                    if ns:
                        data["name_servers"].append(ns)

            return data

        except FileNotFoundError:
            logger.error("whois command not found. Install: sudo apt install whois")
            return {}
        except Exception as e:
            logger.error(f"WHOIS lookup failed: {e}")
            return {}

    # === IP Geolocation (FREE) ===

    def ipapi_lookup(self, ip: str) -> Dict[str, Any]:
        """
        IP geolocation using ip-api.com (FREE - 45 req/min).

        Args:
            ip: IP address

        Returns:
            Geolocation data
        """
        logger.info(f"IP geolocation: {ip}")

        try:
            url = f"http://ip-api.com/json/{ip}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get("status") == "success":
                return {
                    "ip": ip,
                    "country": data.get("country"),
                    "country_code": data.get("countryCode"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "zip": data.get("zip"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "timezone": data.get("timezone"),
                    "isp": data.get("isp"),
                    "org": data.get("org"),
                    "as": data.get("as"),
                    "asname": data.get("asname")
                }

        except Exception as e:
            logger.error(f"IP geolocation failed: {e}")

        return {}

    # === ASN Information (FREE) ===

    def cymru_asn_lookup(self, ip: str) -> Dict[str, Any]:
        """
        ASN lookup using Team Cymru (FREE).

        Args:
            ip: IP address

        Returns:
            ASN information
        """
        logger.info(f"ASN lookup: {ip}")

        try:
            # Reverse IP for DNS query
            reversed_ip = '.'.join(ip.split('.')[::-1])
            query = f"{reversed_ip}.origin.asn.cymru.com"

            # DNS TXT query
            import dns.resolver
            answers = dns.resolver.resolve(query, 'TXT')

            for rdata in answers:
                txt = str(rdata).strip('"')
                parts = txt.split('|')

                if len(parts) >= 5:
                    return {
                        "ip": ip,
                        "asn": parts[0].strip(),
                        "prefix": parts[1].strip(),
                        "country": parts[2].strip(),
                        "registry": parts[3].strip(),
                        "allocated": parts[4].strip()
                    }

        except Exception as e:
            logger.error(f"ASN lookup failed: {e}")

        return {}

    # === GitHub Code Search (FREE) ===

    def github_search(self, query: str, in_code: bool = True) -> List[Dict[str, Any]]:
        """
        Search GitHub for code/repos (FREE with token - 5,000 req/hour).

        Args:
            query: Search query (e.g., "example.com password")
            in_code: Search in code vs repositories

        Returns:
            List of results
        """
        logger.info(f"GitHub search: {query}")

        if not self.github_token:
            logger.warning("GITHUB_TOKEN not set. Limited to 60 req/hour")

        try:
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"

            endpoint = "code" if in_code else "repositories"
            url = f"https://api.github.com/search/{endpoint}"

            response = self.session.get(
                url,
                params={"q": query, "per_page": 30},
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])

            logger.info(f"GitHub found {len(items)} results")

            return [
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "url": item.get("html_url"),
                    "repository": item.get("repository", {}).get("full_name"),
                    "score": item.get("score")
                }
                for item in items
            ]

        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return []

    # === Wayback Machine (FREE) ===

    def wayback_urls(self, domain: str) -> List[str]:
        """
        Fetch URLs from Wayback Machine CDX API (FREE).

        Args:
            domain: Domain to search

        Returns:
            List of archived URLs
        """
        logger.info(f"Wayback Machine search: {domain}")

        try:
            url = f"http://web.archive.org/cdx/search/cdx"
            params = {
                "url": f"{domain}/*",
                "output": "json",
                "collapse": "urlkey",
                "fl": "original",
                "limit": 10000
            }

            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()

            # Skip header row
            urls = [item[0] for item in data[1:] if item]

            logger.info(f"Wayback found {len(urls)} archived URLs")

            return urls

        except Exception as e:
            logger.error(f"Wayback search failed: {e}")
            return []

    # === Have I Been Pwned (FREE) ===

    def hibp_check_breach(self, email: str) -> List[Dict[str, Any]]:
        """
        Check if email in data breaches (FREE).

        Args:
            email: Email address

        Returns:
            List of breaches
        """
        logger.info(f"Checking HIBP for: {email}")

        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            response = self.session.get(
                url,
                headers={"User-Agent": "WilsonsRaider-OSINT"},
                timeout=10
            )

            if response.status_code == 404:
                logger.info("No breaches found")
                return []

            response.raise_for_status()

            breaches = response.json()

            return [
                {
                    "name": breach.get("Name"),
                    "title": breach.get("Title"),
                    "domain": breach.get("Domain"),
                    "breach_date": breach.get("BreachDate"),
                    "added_date": breach.get("AddedDate"),
                    "pwn_count": breach.get("PwnCount"),
                    "description": breach.get("Description"),
                    "data_classes": breach.get("DataClasses")
                }
                for breach in breaches
            ]

        except Exception as e:
            logger.error(f"HIBP check failed: {e}")
            return []

    # === Government Data Sources ===

    def sec_edgar_search(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search SEC EDGAR for company filings (FREE).

        Args:
            company_name: Company name

        Returns:
            List of filings
        """
        logger.info(f"SEC EDGAR search: {company_name}")

        try:
            # Use SEC EDGAR full-text search
            url = "https://efts.sec.gov/LATEST/search-index"
            params = {
                "q": company_name,
                "dateRange": "all"
            }

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            hits = data.get("hits", {}).get("hits", [])

            filings = []
            for hit in hits[:50]:
                source = hit.get("_source", {})
                filings.append({
                    "company": source.get("display_names", [None])[0],
                    "cik": source.get("ciks", [None])[0],
                    "form_type": source.get("file_type"),
                    "filing_date": source.get("file_date"),
                    "description": source.get("file_description")
                })

            logger.info(f"Found {len(filings)} SEC filings")

            return filings

        except Exception as e:
            logger.error(f"SEC EDGAR search failed: {e}")
            return []

    # === Shodan (FREE TIER: 100 queries/month) ===

    def shodan_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search Shodan (FREE tier: 100 queries/month).

        Args:
            query: Shodan search query

        Returns:
            List of results
        """
        if not self.shodan_key:
            logger.warning("SHODAN_API_KEY not set")
            return []

        logger.info(f"Shodan search: {query}")

        try:
            url = "https://api.shodan.io/shodan/host/search"
            params = {
                "key": self.shodan_key,
                "query": query
            }

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            matches = data.get("matches", [])

            logger.info(f"Shodan found {len(matches)} results")

            return [
                {
                    "ip": match.get("ip_str"),
                    "port": match.get("port"),
                    "hostnames": match.get("hostnames"),
                    "domains": match.get("domains"),
                    "org": match.get("org"),
                    "data": match.get("data"),
                    "product": match.get("product"),
                    "version": match.get("version"),
                    "vulns": list(match.get("vulns", []))
                }
                for match in matches
            ]

        except Exception as e:
            logger.error(f"Shodan search failed: {e}")
            return []

    # === Comprehensive OSINT Report ===

    def comprehensive_osint(self, domain: str) -> Dict[str, Any]:
        """
        Run comprehensive OSINT collection on a domain.

        Args:
            domain: Target domain

        Returns:
            Complete OSINT report
        """
        logger.info(f"Running comprehensive OSINT on {domain}")

        report = {
            "target": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "certificate_transparency": {},
            "dns": {},
            "whois": {},
            "subdomains": [],
            "archived_urls": [],
            "ip_info": {},
            "github_exposure": []
        }

        # Certificate Transparency
        certs = self.crtsh_search(domain)
        report["certificate_transparency"] = {
            "count": len(certs),
            "certificates": certs[:100]  # Limit for report size
        }

        # Extract subdomains from certs
        subdomains = set()
        for cert in certs:
            names = cert.get("name_value", "").split('\n')
            for name in names:
                name = name.strip().replace('*', '')
                if name and domain in name:
                    subdomains.add(name)

        report["subdomains"] = list(subdomains)

        # DNS records
        for record_type in ["A", "AAAA", "MX", "NS", "TXT"]:
            records = self.dns_lookup(domain, record_type)
            if records:
                report["dns"][record_type] = records

        # WHOIS
        report["whois"] = self.whois_lookup(domain)

        # Get IP from DNS
        a_records = report["dns"].get("A", [])
        if a_records:
            ip = a_records[0]

            # IP Geolocation
            report["ip_info"]["geolocation"] = self.ipapi_lookup(ip)

            # ASN
            report["ip_info"]["asn"] = self.cymru_asn_lookup(ip)

        # Wayback Machine
        archived_urls = self.wayback_urls(domain)
        report["archived_urls"] = archived_urls[:1000]  # Limit

        # GitHub code search
        github_results = self.github_search(f"{domain}", in_code=True)
        report["github_exposure"] = github_results

        logger.info(f"OSINT collection complete: {len(subdomains)} subdomains, {len(archived_urls)} archived URLs")

        return report
