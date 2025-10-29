from rich.theme import Theme

# The color theme for the UI
THEME = Theme({
    "banner": "bold gold1 on black",
    "header": "bold purple on black",
    "subheader": "bold cyan on black",
    "info": "white on black",
    "success": "bold green on black",
    "warning": "bold yellow on black",
    "error": "bold red on black",
    "vulnerability.critical": "bold red on black",
    "vulnerability.high": "bold magenta on black",
    "vulnerability.medium": "bold yellow on black",
    "vulnerability.low": "cyan on black",
    "red_team": "bold red on black",
    "blue_team": "bold blue on black",
})

# The thematic names for different tool stages
NAMES = {
    'tool': "Wilsons Raiders - Chimera Edition",
    'tool_desc': "An AI-enhanced, distributed, and adaptive security assessment platform.",
    'recon': "The Raider's Gaze (Reconnaissance)",
    'scanning': "The Breach Protocol (Active Scanning)",
    'reporting': "The War Report (Reporting)",
    'ai_prio': "The Oracle's Verdict (AI Analysis) - Asset Prioritization",
    'ai_killchain': "The Oracle's Verdict (AI Analysis) - Kill Chain Weaving",
    'ai_feedback': "The All-Father's Wisdom (AI Feedback)"
}

def get_name(key):
    return NAMES.get(key, key.upper())

