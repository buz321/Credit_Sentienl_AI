import requests
import json
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import time
import re

class SECFilingFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Credit Sentinel AI research.contact@example.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        self.base_url = "https://www.sec.gov"
        self.edgar_base_url = "https://www.sec.gov/Archives/edgar"
        
    def format_cik(self, cik: str) -> str:
        """Format CIK to 10 digits with leading zeros."""
        return str(cik).zfill(10)
        
    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK number for a given ticker symbol."""
        try:
            time.sleep(0.1)  # SEC rate limit
            response = requests.get(
                f"{self.base_url}/files/company_tickers.json",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            
            for entry in data.values():
                if entry['ticker'].upper() == ticker.upper():
                    return self.format_cik(entry['cik_str'])
            print(f"Could not find CIK for ticker {ticker}")
            return None
        except Exception as e:
            print(f"Error getting CIK: {e}")
            return None

    def get_latest_filing(self, ticker: str, form_type: str = "10-K") -> Optional[str]:
        """Get the latest 10-K or 10-Q filing for a company."""
        try:
            cik = self.get_cik_from_ticker(ticker)
            if not cik:
                return None

            # Get company submissions from EDGAR
            time.sleep(0.1)  # SEC rate limit
            submissions_url = f"{self.edgar_base_url}/data/{int(cik)}/index.json"
            response = requests.get(submissions_url, headers=self.headers)
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from SEC API: {e}")
                print(f"Response content: {response.text[:200]}...")
                return None

            # Find the latest 10-K/10-Q filing
            filings = data.get('directory', {}).get('item', [])
            if not filings:
                print("No filings found")
                return None

            # Sort filings by date (most recent first)
            filings.sort(key=lambda x: x.get('last-modified', ''), reverse=True)
            
            # Find the latest matching filing
            for filing in filings:
                name = filing.get('name', '').lower()
                if form_type.lower() in name and '.htm' in name:
                    file_url = f"{self.edgar_base_url}/data/{int(cik)}/{filing['name']}"
                    print(f"Found {form_type} filing: {file_url}")
                    
                    time.sleep(0.1)  # SEC rate limit
                    filing_response = requests.get(file_url, headers=self.headers)
                    
                    if filing_response.status_code == 200:
                        content = filing_response.text
                        if content and len(content) > 1000:  # Basic validation
                            return content
                    break

            print(f"Could not find {form_type} filing content")
            return None
            
        except Exception as e:
            print(f"Error fetching filing: {e}")
            return None

def get_filing_text(ticker: str) -> Optional[str]:
    """Interface function to get the latest filing text."""
    fetcher = SECFilingFetcher()
    
    # Try 10-K first, then 10-Q if no 10-K is found
    filing = fetcher.get_latest_filing(ticker, "10-K")
    if not filing:
        print("No 10-K found, trying 10-Q...")
        filing = fetcher.get_latest_filing(ticker, "10-Q")
        
    if not filing:
        print(f"Could not retrieve any filings for {ticker}")
        return None
        
    return filing
