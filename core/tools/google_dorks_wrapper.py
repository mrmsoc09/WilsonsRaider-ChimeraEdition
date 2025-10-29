import requests
from bs4 import BeautifulSoup
from core import ui

def google_search(query: str, num_results: int = 5) -> list[str]:
    """
    Performs a basic Google search and returns a list of result URLs.
    Note: This is a very basic implementation and is prone to CAPTCHAs and rate-limiting.
    For robust use, consider a dedicated Google Search API or a more sophisticated scraper.
    """
    ui.print_info(f"Performing Google search for: '{query}'...")
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for g in soup.find_all(class_='g'):
            a_tag = g.find('a')
            if a_tag and a_tag.get('href'):
                link = a_tag['href']
                if link.startswith("http") and "google.com/recaptcha" not in link:
                    links.append(link)
        ui.print_success(f"Found {len(links)} results for '{query}'.")
        return links
    except requests.exceptions.RequestException as e:
        ui.print_error(f"Google search failed for '{query}': {e}")
        return []

def run_google_dorks(target: str, dorks: list[str]) -> dict:
    """
    Executes a list of Google Dorks against a target and returns the results.
    """
    ui.print_info(f"Running Google Dorks for target: {target}...")
    all_results = {}
    for dork in dorks:
        query = f"site:{target} {dork}"
        results = google_search(query)
        if results:
            all_results[dork] = results
    
    if all_results:
        ui.print_success(f"Google Dorks completed for {target}. Found results for {len(all_results)} dorks.")
    else:
        ui.print_warning(f"Google Dorks completed for {target}. No results found.")

    return {"status": "success", "results": all_results}
