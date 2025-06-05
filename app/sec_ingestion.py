import requests

def get_filing_text(ticker):
    headers = {
        'User-Agent': 'CreditSentinelAI/0.1 (your_email@example.com)'
    }

    cik_lookup_url = "https://www.sec.gov/files/company_tickers.json"
    cik_lookup = requests.get(cik_lookup_url, headers=headers).json()

    cik = None
    for entry in cik_lookup.values():
        if entry['ticker'].lower() == ticker.lower():
            cik = str(entry['cik_str']).zfill(10)
            break

    if cik is None:
        return None

    # Get recent submissions
    sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    sub_resp = requests.get(sub_url, headers=headers).json()

    try:
        accession = sub_resp["filings"]["recent"]["accessionNumber"][0]
        doc_name = sub_resp["filings"]["recent"]["primaryDocument"][0]
        accession_nodash = accession.replace("-", "")
        filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_nodash}/{doc_name}"
        print("Filing URL:", filing_url)

        filing_text = requests.get(filing_url, headers=headers).text
        return filing_text
    except Exception as e:
        print("Error extracting filing info:", e)
        return None
