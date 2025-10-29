from core.correlation.engine import CorrelationEngine

def test_correlation_basic():
    ce = CorrelationEngine()
    raw = [
        {"type": "subdomain", "value": "dev.example.com", "source": "subfinder"},
        {"type": "subdomain", "value": "dev.example.com", "source": "crt.sh"},
        {"type": "apikey", "value": "AKIA...", "source": "repo_scan"},
    ]
    out = ce.process(raw)
    assert "assets" in out
    assert out["assets"]["subdomains"], "Expect subdomains categorized"
    assert out["assets"]["secrets"], "Expect secrets categorized"
