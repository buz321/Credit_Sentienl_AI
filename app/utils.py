# app/utils.py

from bs4 import BeautifulSoup

def clean_filing_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text
