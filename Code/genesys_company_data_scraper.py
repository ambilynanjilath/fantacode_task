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
    """
    Reads the input CSV file containing company URLs.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A pandas DataFrame containing
                      the data from the CSV file.
    """
    return pd.read_csv(file_path)

def initialize_details(url: str, region: str) -> Dict:
    """
    Initialize the details dictionary with None values.

    Args:
        url (str): The product URL to be included in the details.
        region (str): The region to be included in the details.

    Returns:
        Dict: A dictionary with initialized fields set to None,
              except for 'product_url' and 'region'.
    """
    return {
        'company_name': None,
        'industry': None,
        'location': None,
        'partners': None,
        'person_quoted': None,
        'product_url': url,
        'region': region  
    }

def get_soup(url: str) -> BeautifulSoup:
    """
    Create BeautifulSoup object from URL with rotating user agent.

    Args:
        url (str): The URL to fetch and parse.

    Returns:
        BeautifulSoup: A BeautifulSoup object containing the parsed HTML
                       content of the page.
    """
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')

def extract_company_name(paragraph) -> Optional[str]:
    """
    Extract company name from paragraph.

    This function looks for a 'Customer:' label in the paragraph and 
    retrieves the text of the link that follows it as the company name.

    Args:
        paragraph: A BeautifulSoup tag object representing the paragraph 
                   containing the company information.

    Returns:
        Optional[str]: The company name if found, otherwise None.
    """
    if 'Customer:' in paragraph.text:
        company_link = paragraph.find('a')
        if company_link:
            return company_link.text.strip()
    return None

def extract_field(paragraph, field_name: str) -> Optional[str]:
    """
    Extract industry value from paragraph.

    This function looks for the specified field name in the paragraph text
    and returns the value that follows it, or None if the field is not found.

    Args:
        paragraph: A BeautifulSoup tag object representing the paragraph 
                   containing the field information.
        field_name: The name of the field to extract (e.g., 'Industry', 
                    'Location').

    Returns:
        Optional[str]: The extracted field value if found, otherwise None.
    """
    if f'{field_name}:' in paragraph.text:
        text = paragraph.text.split(f'{field_name}:')[-1].strip()
        return text if text else None
    return None

def extract_partners(soup) -> Optional[List[str]]:
    """
    Extract partner details from soup, 
    handling both old and new HTML structures.

    This function searches for two different container classes:
    'cs-partner-container' and 'cs-custom-container custom-plain',
    in the soup and extracts the partner details.

    Args:
        soup: A BeautifulSoup object containing the parsed HTML
              of the page.

    Returns:
        Optional[List[str]]: A list of partner names if found,
                             otherwise None.
    """
    
    # Check for the first container with class 
    # 'cs-partner-container'
    partner_container = soup.find(
        'div', 
        class_='cs-sidebar-item cs-partner-container'
    )
    if partner_container:
        partners = partner_container.find_all('a')
        partner_list = [
            partner.text.strip() for partner in partners
        ]
        if partner_list:
            return partner_list

    # Check for the seond container with class 
    # 'cs-custom-container custom-plain'
    partner_container_new = soup.find(
        'div', 
        class_='cs-sidebar-item cs-custom-container custom-plain'
    )
    if partner_container_new:
        partners = partner_container_new.find_all('a')
        partner_list = [
            partner.text.strip() for partner in partners
        ]
        if partner_list:
            return partner_list

    return None

def extract_quote(soup) -> Optional[str]:
    """
    Extract person quoted from soup, 
    handling both old and new HTML structures.

    This function checks for two possible HTML structures 
    in the provided BeautifulSoup object. It first looks for 
    the original structure with the class 'quote-speaker', 
    and if not found, it checks for the new structure with 
    the class 'cq_block_speaker'.

    Args:
        soup: A BeautifulSoup object containing the parsed 
              HTML of the page.

    Returns:
        Optional[str]: The name or quote of the person quoted 
                        if found, otherwise None.
    """
    
    # Check for the original structure
    quote_speaker = soup.find(
        'div', class_='quote-speaker'
    )
    if quote_speaker:
        quote_info = quote_speaker.find('p')
        if quote_info and '—' in quote_info.text:
            return quote_info.text.split('—')[1].strip()

    # Check for the new structure with the class 'cq_block_speaker'
    quote_speaker_new = soup.find(
        'div', class_='wpb_content_element customer_quote_block'
    )
    if quote_speaker_new:
        speaker_info = quote_speaker_new.find(
            'p', class_='cq_block_speaker'
        )
        if speaker_info:
            return speaker_info.text.strip()

    return None


def extract_sidebar_info(soup, details: Dict) -> Dict:
    """
    Extract information from sidebar.

    This function extracts the company name, industry, and location 
    from the sidebar of a given BeautifulSoup object. It looks for 
    specific HTML elements and adds the extracted values to the 
    provided details dictionary.

    Args:
        soup: A BeautifulSoup object containing the parsed HTML.
        details: A dictionary to store extracted information like 
                 company name, industry, and location.

    Returns:
        Dict: The updated details dictionary with extracted information.
    """
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
    """
    Main function to extract all details from a URL.

    This function orchestrates the process of extracting various 
    details such as company name, industry, location, partners, 
    and person quoted from a given URL. It uses the provided region 
    and URL to gather all the required information and returns a 
    dictionary containing these details.

    Args:
        url (str): The URL from which the details are to be extracted.
        region (str): The region associated with the company.

    Returns:
        Dict: A dictionary containing extracted details such as company 
              name, industry, location, partners, and person quoted.
    """
    details = initialize_details(url, region)  
    soup = get_soup(url)
    
    details = extract_sidebar_info(soup, details)
    details['partners'] = extract_partners(soup)
    details['person_quoted'] = extract_quote(soup)
    
    return details

def append_to_csv(data: Dict, output_path: str, first_write: bool):
    """
    Append a single record to a CSV file.

    This function appends a single record (provided as a dictionary) 
    to an existing CSV file. It checks whether it is the first write 
    to the file and includes a header if necessary.

    Args:
        data (Dict): The data to be appended to the CSV file.
        output_path (str): The path to the output CSV file.
        first_write (bool): A flag indicating whether it is the 
                            first write to the CSV file (for 
                            including the header).

    Returns:
        None
    """
    df = pd.DataFrame([data])
    df.to_csv(output_path, mode='a', 
              header=first_write, index=False)

def process_urls(df: pd.DataFrame, output_path: str):
    """
    Process URLs and save data incrementally.

    This function processes a DataFrame containing company URLs and 
    their associated regions. For each URL, it extracts details, 
    applies a random delay between requests, and saves the results 
    incrementally to a CSV file. The first write includes the header.

    Args:
        df (pd.DataFrame): A DataFrame containing company URLs and 
                            regions to be processed.
        output_path (str): The path to the output CSV file where 
                           the results will be saved.

    Returns:
        None
    """
    first_write = True
    for _, row in df.iterrows():
        try:
            company_url = row['company_url']
            # Read region from the CSV file
            region = row['region']  
            
            # Add random delay between 2 to 5 seconds
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            # Pass region to the details function
            details = extract_details(company_url, region)  
            append_to_csv(details, output_path, first_write)
            
            print(f"Successfully scraped and saved data for URL: {company_url}")
            print(f"Waited {delay:.2f} seconds before this request")
            
            first_write = False
            
        except Exception as e:
            print(f"Error processing URL {company_url}: {str(e)}")
            continue


def main():
    """Main function to orchestrate the scraping process.

    This function serves as the entry point for the scraping process. 
    It reads the input CSV containing company URLs, processes each 
    URL to extract relevant data, and saves the results to an output 
    CSV file. The function also prints a completion message upon 
    successful execution.

    Args:
        None

    Returns:
        None
    """
    input_path = 'Data/company_links.csv' 
    output_path = 'Data/company_data.csv'  
    
    df = read_input_csv(input_path)
    process_urls(df, output_path)
    print(f"Scraping complete! All data has been saved to '{output_path}'")

if __name__ == "__main__":
    main()
