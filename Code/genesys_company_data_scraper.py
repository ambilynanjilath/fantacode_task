import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import random
import time

# List of user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
]

def read_input_csv(file_path: str) -> pd.DataFrame:
    """Read the input CSV file containing company URLs."""
    return pd.read_csv(file_path)

def initialize_details(url: str, region: str) -> Dict:
    """Initialize the details dictionary with None values."""
    return {
        'company_name': None,
        'industry': None,
        'location': None,
        'partners': None,
        'person_quoted': None,
        'product_url': url,
        'region': region  # Add region to the dictionary
    }

def get_soup(url: str) -> BeautifulSoup:
    """Create BeautifulSoup object from URL with rotating user agent."""
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')

def extract_company_name(paragraph) -> Optional[str]:
    """Extract company name from paragraph."""
    if 'Customer:' in paragraph.text:
        company_link = paragraph.find('a')
        if company_link:
            return company_link.text.strip()
    return None

def extract_field(paragraph, field_name: str) -> Optional[str]:
    """Extract field value from paragraph."""
    if f'{field_name}:' in paragraph.text:
        text = paragraph.text.split(f'{field_name}:')[-1].strip()
        return text if text else None
    return None

def extract_partners(soup) -> Optional[List[str]]:
    """Extract partner details from soup."""
    partner_container = soup.find('div', class_='cs-sidebar-item cs-partner-container')
    if partner_container:
        partners = partner_container.find_all('a')
        partner_list = [partner.text.strip() for partner in partners]
        return partner_list if partner_list else None
    return None

def extract_quote(soup) -> Optional[str]:
    """Extract person quoted from soup."""
    quote_speaker = soup.find('div', class_='quote-speaker')
    if quote_speaker:
        quote_info = quote_speaker.find('p')
        if quote_info and '—' in quote_info.text:
            return quote_info.text.split('—')[1].strip()
    return None

def extract_sidebar_info(soup, details: Dict) -> Dict:
    """Extract information from sidebar."""
    sidebar_item = soup.find('div', class_='cs-sidebar-item')
    if sidebar_item:
        paragraphs = sidebar_item.find_all('p', class_='mb-0')
        for p in paragraphs:
            company_name = extract_company_name(p)
            if company_name:
                details['company_name'] = company_name
            
            industry = extract_field(p, 'Industry')
            if industry:
                details['industry'] = industry
            
            location = extract_field(p, 'Location')
            if location:
                details['location'] = location
    return details

def extract_details(url: str, region: str) -> Dict:
    """Main function to extract all details from a URL."""
    details = initialize_details(url, region)  # Pass region to the details
    soup = get_soup(url)
    
    details = extract_sidebar_info(soup, details)
    details['partners'] = extract_partners(soup)
    details['person_quoted'] = extract_quote(soup)
    
    return details

def append_to_csv(data: Dict, output_path: str, first_write: bool):
    """Append a single record to CSV file."""
    df = pd.DataFrame([data])
    df.to_csv(output_path, mode='a', header=first_write, index=False)

def process_urls(df: pd.DataFrame, output_path: str):
    """Process URLs and save data incrementally."""
    first_write = True
    for _, row in df.iterrows():
        try:
            company_url = row['company_url']
            region = row['region']  # Read region from the CSV file
            
            # Add random delay between 2 to 5 seconds
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            details = extract_details(company_url, region)  # Pass region to the details function
            append_to_csv(details, output_path, first_write)
            
            print(f"Successfully scraped and saved data for URL: {company_url}")
            print(f"Waited {delay:.2f} seconds before this request")
            
            first_write = False
            
        except Exception as e:
            print(f"Error processing URL {company_url}: {str(e)}")
            continue

def main():
    """Main function to orchestrate the scraping process."""
    input_path = '/home/user/Documents/fantacode_task/Data/company_links.csv'  # Update the path
    output_path = '/home/user/Documents/fantacode_task/Data/company_data.csv'  # Update the path
    
    df = read_input_csv(input_path)
    process_urls(df, output_path)
    print(f"Scraping complete! All data has been saved to '{output_path}'")

if __name__ == "__main__":
    main()
