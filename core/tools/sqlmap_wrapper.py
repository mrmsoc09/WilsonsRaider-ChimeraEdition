"""SQLMap Wrapper - Production-Grade SQL Injection Testing

Comprehensive wrapper for SQLMap with automated injection testing,
database enumeration, and data extraction capabilities.
Version: 1.0.0
"""

import subprocess
import json
import logging
import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLMapWrapper:
    """Production-grade SQLMap SQL injection testing wrapper."""

    def __init__(self,
                 output_dir: str = "/tmp/sqlmap",
                 api_mode: bool = False,
                 risk_level: int = 1,
                 verbosity: int = 1):
        """
        Initialize SQLMap wrapper.

        Args:
            output_dir: Output directory for session files
            api_mode: Use SQLMap API server
            risk_level: Test risk level (1-3, higher = more aggressive)
            verbosity: Output verbosity (0-6)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_mode = api_mode
        self.risk_level = risk_level
        self.verbosity = verbosity

        # Check if sqlmap is installed
        try:
            subprocess.run(['sqlmap', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError("SQLMap not installed. Install from: https://github.com/sqlmapproject/sqlmap")

    def test_injection(self,
                       url: str,
                       method: str = "GET",
                       data: Optional[str] = None,
                       cookies: Optional[str] = None,
                       headers: Optional[Dict[str, str]] = None,
                       dbms: Optional[str] = None,
                       technique: Optional[str] = None,
                       batch: bool = True,
                       timeout: int = 1800) -> Dict[str, Any]:
        """
        Test for SQL injection vulnerabilities.

        Args:
            url: Target URL
            method: HTTP method
            data: POST/PUT data
            cookies: Session cookies
            headers: Custom headers
            dbms: Force DBMS (MySQL, PostgreSQL, MSSQL, Oracle, etc.)
            technique: SQL injection techniques (B=Boolean, E=Error, U=Union, S=Stacked, T=Time, Q=Query)
            batch: Never ask for user input (automated mode)
            timeout: Maximum execution time

        Returns:
            Dict with injection results
        """
        logger.info(f"Starting SQLMap injection test on {url}")

        session_file = self.output_dir / f"session_{int(time.time())}.sqlite"

        command = [
            'sqlmap',
            '-u', url,
            '--batch' if batch else '',
            '--risk', str(self.risk_level),
            '--level', str(min(self.risk_level + 1, 5)),  # Level 1-5
            '-v', str(self.verbosity),
            '-s', str(session_file),
            '--output-dir', str(self.output_dir),
            '--flush-session',
        ]

        # Remove empty strings
        command = [c for c in command if c]

        if method.upper() != "GET":
            command.extend(['--method', method.upper()])

        if data:
            command.extend(['--data', data])

        if cookies:
            command.extend(['--cookie', cookies])

        if headers:
            for key, value in headers.items():
                command.extend(['--header', f"{key}: {value}"])

        if dbms:
            command.extend(['--dbms', dbms])

        if technique:
            command.extend(['--technique', technique])

        # Randomize User-Agent for OPSEC
        command.append('--random-agent')

        # Smart detection
        command.extend(['--smart', '--identify-waf'])

        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, 'SQLMAP_DISABLE_PRECON': '1'}
            )

            duration = time.time() - start_time

            # Parse output for vulnerability confirmation
            vulnerable = self._check_vulnerability(result.stdout)

            if vulnerable:
                logger.warning(f"SQL injection found on {url}")
            else:
                logger.info(f"No SQL injection found on {url}")

            return {
                "url": url,
                "vulnerable": vulnerable,
                "duration": duration,
                "output": result.stdout,
                "session_file": str(session_file),
                "details": self._parse_output(result.stdout)
            }

        except subprocess.TimeoutExpired:
            logger.error(f"SQLMap test timed out after {timeout}s")
            return {"error": "timeout", "url": url, "vulnerable": False}
        except Exception as e:
            logger.error(f"SQLMap test failed: {e}")
            return {"error": str(e), "url": url, "vulnerable": False}

    def enumerate_databases(self,
                            url: str,
                            data: Optional[str] = None,
                            cookies: Optional[str] = None) -> Dict[str, Any]:
        """
        Enumerate databases after confirming injection.

        Args:
            url: Vulnerable URL
            data: POST data
            cookies: Session cookies

        Returns:
            Dict with database list
        """
        logger.info(f"Enumerating databases on {url}")

        command = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--dbs',
            '--output-dir', str(self.output_dir),
        ]

        if data:
            command.extend(['--data', data])

        if cookies:
            command.extend(['--cookie', cookies])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600
            )

            databases = self._extract_databases(result.stdout)

            logger.info(f"Found {len(databases)} databases")

            return {
                "url": url,
                "databases": databases,
                "count": len(databases)
            }

        except Exception as e:
            logger.error(f"Database enumeration failed: {e}")
            return {"error": str(e), "url": url, "databases": []}

    def enumerate_tables(self,
                         url: str,
                         database: str,
                         data: Optional[str] = None,
                         cookies: Optional[str] = None) -> Dict[str, Any]:
        """
        Enumerate tables in a database.

        Args:
            url: Vulnerable URL
            database: Target database name
            data: POST data
            cookies: Session cookies

        Returns:
            Dict with table list
        """
        logger.info(f"Enumerating tables in database {database}")

        command = [
            'sqlmap',
            '-u', url,
            '--batch',
            '-D', database,
            '--tables',
            '--output-dir', str(self.output_dir),
        ]

        if data:
            command.extend(['--data', data])

        if cookies:
            command.extend(['--cookie', cookies])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600
            )

            tables = self._extract_tables(result.stdout)

            logger.info(f"Found {len(tables)} tables in {database}")

            return {
                "url": url,
                "database": database,
                "tables": tables,
                "count": len(tables)
            }

        except Exception as e:
            logger.error(f"Table enumeration failed: {e}")
            return {"error": str(e), "url": url, "tables": []}

    def dump_table(self,
                   url: str,
                   database: str,
                   table: str,
                   columns: Optional[List[str]] = None,
                   data: Optional[str] = None,
                   cookies: Optional[str] = None,
                   limit_rows: int = 100) -> Dict[str, Any]:
        """
        Dump data from a table.

        Args:
            url: Vulnerable URL
            database: Database name
            table: Table name
            columns: Specific columns to dump
            data: POST data
            cookies: Session cookies
            limit_rows: Maximum rows to dump

        Returns:
            Dict with dumped data
        """
        logger.info(f"Dumping table {database}.{table}")

        command = [
            'sqlmap',
            '-u', url,
            '--batch',
            '-D', database,
            '-T', table,
            '--dump',
            '--start', '1',
            '--stop', str(limit_rows),
            '--output-dir', str(self.output_dir),
        ]

        if columns:
            command.extend(['-C', ','.join(columns)])

        if data:
            command.extend(['--data', data])

        if cookies:
            command.extend(['--cookie', cookies])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=1800
            )

            # Find CSV dump file
            csv_files = list(self.output_dir.rglob(f"*{table}*.csv"))
            dump_data = []

            if csv_files:
                import csv
                with open(csv_files[0], 'r') as f:
                    reader = csv.DictReader(f)
                    dump_data = list(reader)

            logger.info(f"Dumped {len(dump_data)} rows from {database}.{table}")

            return {
                "url": url,
                "database": database,
                "table": table,
                "rows": dump_data,
                "count": len(dump_data),
                "csv_file": str(csv_files[0]) if csv_files else None
            }

        except Exception as e:
            logger.error(f"Table dump failed: {e}")
            return {"error": str(e), "url": url, "rows": []}

    def os_shell(self,
                 url: str,
                 data: Optional[str] = None,
                 cookies: Optional[str] = None) -> Dict[str, Any]:
        """
        Attempt to get OS shell access (very intrusive).

        Args:
            url: Vulnerable URL
            data: POST data
            cookies: Session cookies

        Returns:
            Dict with shell access results
        """
        logger.warning(f"Attempting OS shell access on {url} (INTRUSIVE)")

        command = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--os-shell',
            '--output-dir', str(self.output_dir),
        ]

        if data:
            command.extend(['--data', data])

        if cookies:
            command.extend(['--cookie', cookies])

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600,
                input="whoami\nexit\n"  # Test commands
            )

            shell_obtained = "os-shell>" in result.stdout

            return {
                "url": url,
                "shell_obtained": shell_obtained,
                "output": result.stdout
            }

        except Exception as e:
            logger.error(f"OS shell attempt failed: {e}")
            return {"error": str(e), "url": url, "shell_obtained": False}

    def _check_vulnerability(self, output: str) -> bool:
        """Check if SQL injection was found."""
        indicators = [
            "is vulnerable",
            "Type: ",
            "Payload: ",
            "injectable",
        ]
        return any(indicator in output for indicator in indicators)

    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse SQLMap output for details."""
        details = {
            "injection_type": None,
            "dbms": None,
            "payload": None,
            "waf_detected": False
        }

        for line in output.split('\n'):
            if "Type:" in line:
                details["injection_type"] = line.split("Type:")[1].strip()
            elif "back-end DBMS:" in line:
                details["dbms"] = line.split("back-end DBMS:")[1].strip()
            elif "Payload:" in line:
                details["payload"] = line.split("Payload:")[1].strip()
            elif "WAF" in line and "detected" in line.lower():
                details["waf_detected"] = True

        return details

    def _extract_databases(self, output: str) -> List[str]:
        """Extract database names from output."""
        databases = []
        in_db_section = False

        for line in output.split('\n'):
            if "available databases" in line.lower():
                in_db_section = True
                continue

            if in_db_section:
                if line.strip().startswith('[*]'):
                    db_name = line.strip().replace('[*]', '').strip()
                    if db_name:
                        databases.append(db_name)
                elif not line.strip() or line.startswith('['):
                    in_db_section = False

        return databases

    def _extract_tables(self, output: str) -> List[str]:
        """Extract table names from output."""
        tables = []
        in_table_section = False

        for line in output.split('\n'):
            if "table" in line.lower() and (":" in line or "|" in line):
                in_table_section = True
                continue

            if in_table_section:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        table_name = parts[1].strip()
                        if table_name and table_name not in ['Table', '']:
                            tables.append(table_name)
                elif not line.strip():
                    in_table_section = False

        return tables
