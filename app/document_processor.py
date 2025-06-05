from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple

class SECDocumentProcessor:
    IMPORTANT_SECTIONS = {
        'risk_factors': [
            r'Item\s*1A\.?\s*Risk\s*Factors',
            r'Risk\s*Factors',
            r'ITEM\s*1A\s*[-–]\s*RISK\s*FACTORS',
        ],
        'mda': [
            r"Item\s*7\.?\s*Management's\s*Discussion\s*and\s*Analysis",
            r"Management's\s*Discussion\s*and\s*Analysis",
            r"ITEM\s*7\s*[-–]\s*MANAGEMENT'S\s*DISCUSSION",
        ],
        'liquidity': [
            r'Liquidity\s*and\s*Capital\s*Resources',
            r'Item\s*7\.?\s*Liquidity',
            r'LIQUIDITY\s*AND\s*CAPITAL\s*RESOURCES',
        ]
    }

    def __init__(self):
        self.sections: Dict[str, str] = {}
        self.raw_text: str = ""

    def clean_html(self, html_content: str) -> str:
        """Clean HTML content and extract meaningful text."""
        if not html_content:
            print("Warning: Empty HTML content provided")
            return ""
            
        try:
            # First try parsing as XML
            try:
                soup = BeautifulSoup(html_content, "xml")
            except:
                # If XML parsing fails, try HTML
                soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove unwanted elements
            for element in soup(["script", "style", "noscript", "iframe", "header", "footer", "img"]):
                element.decompose()
                
            # Remove hidden elements
            for element in soup.find_all(style=re.compile(r"display:\s*none")):
                element.decompose()
                
            # Remove tables that are likely not relevant (e.g., navigation, layout tables)
            for table in soup.find_all('table'):
                if table.get('role') == 'presentation' or 'nav' in str(table.get('class', [])):
                    table.decompose()
                    
            # Get text while preserving structure
            text_blocks = []
            for element in soup.stripped_strings:
                text = element.strip()
                if text and len(text) > 1:  # Skip single characters
                    # Clean up text
                    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                    text = re.sub(r'[\n\r\t]+', ' ', text)  # Remove newlines and tabs
                    text_blocks.append(text)
                    
            cleaned_text = "\n".join(text_blocks)
            if not cleaned_text:
                print("Warning: No text extracted from HTML")
                return ""
                
            return cleaned_text
            
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            return html_content if html_content else ""

    def extract_section(self, text: str, section_patterns: List[str], 
                       next_section_patterns: Optional[List[str]] = None) -> Optional[str]:
        """Extract a section from text using regex patterns."""
        try:
            if not text:
                print("Warning: No text provided for section extraction")
                return None
                
            if not next_section_patterns:
                next_section_patterns = [
                    r'Item\s*\d+[A-Z]?\.?',  # Match "Item X" or "Item XA"
                    r'PART\s+[IVX]+',        # Match "PART I", "PART II", etc.
                    r'ITEM\s*\d+[A-Z]?',     # Match "ITEM X" or "ITEM XA"
                ]
                
            # Find start of section
            start_pos = -1
            start_pattern = None
            for pattern in section_patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
                if matches:
                    # Take the last match if multiple found (often more accurate in SEC filings)
                    match = matches[-1]
                    start_pos = match.start()
                    start_pattern = pattern
                    break
                    
            if start_pos == -1:
                print(f"Warning: Could not find section start using patterns: {section_patterns}")
                return None
                
            # Find end of section
            end_pos = len(text)
            search_start = start_pos + len(re.search(start_pattern, text[start_pos:], re.IGNORECASE).group(0))
            
            for pattern in next_section_patterns:
                match = re.search(pattern, text[search_start:], re.IGNORECASE)
                if match:
                    end_pos = search_start + match.start()
                    break
                    
            section_text = text[start_pos:end_pos].strip()
            if not section_text:
                print("Warning: Extracted empty section")
                return None
                
            # Clean up the section text
            section_text = re.sub(r'^\s*(?:Item\s+\d+[A-Z]?\.?|PART\s+[IVX]+|ITEM\s+\d+[A-Z]?)[^\n]*\n', '', section_text)
            section_text = re.sub(r'\s+', ' ', section_text)
            
            return section_text
            
        except Exception as e:
            print(f"Error extracting section: {e}")
            return None

    def process_filing(self, html_content: str) -> None:
        """Process the filing and extract important sections."""
        try:
            if not html_content:
                print("Warning: Empty HTML content provided")
                return
                
            self.raw_text = self.clean_html(html_content)
            if not self.raw_text:
                print("Warning: No text extracted from HTML")
                return
                
            # Extract each important section
            for section_name, patterns in self.IMPORTANT_SECTIONS.items():
                section_text = self.extract_section(self.raw_text, patterns)
                if section_text:
                    self.sections[section_name] = section_text
                    print(f"Found {section_name} section")
                else:
                    print(f"Warning: Could not find {section_name} section")
                    
        except Exception as e:
            print(f"Error processing filing: {e}")

    def get_relevant_context(self, question: str) -> Optional[str]:
        """Get the most relevant section based on the question."""
        try:
            if not self.sections and not self.raw_text:
                print("Warning: No sections or raw text available")
                return None
                
            if not question:
                print("Warning: Empty question provided")
                return None
                
            # Simple keyword matching for now
            question = question.lower()
            if any(word in question for word in ['risk', 'threat', 'warning', 'concern', 'adverse']):
                context = self.sections.get('risk_factors')
            elif any(word in question for word in ['liquidity', 'cash', 'capital', 'debt', 'funding']):
                context = self.sections.get('liquidity')
            elif any(word in question for word in ['management', 'performance', 'financial', 'operation', 'revenue']):
                context = self.sections.get('mda')
            else:
                # If no clear match, return concatenated sections
                context = "\n\n".join(self.sections.values()) if self.sections else None
                
            # Fall back to raw text if no sections found
            if not context and self.raw_text:
                print("Warning: No matching sections found, using raw text")
                return self.raw_text[:50000]  # Return first 50K chars if no sections found
                
            return context
            
        except Exception as e:
            print(f"Error getting relevant context: {e}")
            return None 