# Genesys Company Data Scraping Project

This project involves scraping company data from the Genesys website and processing it into a structured CSV format for analysis. It includes a web scraping pipeline built with Playwright and BeautifulSoup, and a data cleaning step using pandas.

## Scripts Overview

### 1. genesys_company_link_scraper.py

This script scrapes customer story links and their regions from the Genesys website.

#### Key Functions

* `select_genesys_cloud_filters(page)`:
  * Expands the filter options and selects checkboxes for "Genesys Cloud" and "Genesys Cloud EX."

* `scrape_customer_story_links_and_regions(page)`:
  * Scrolls through the webpage to extract customer story links and region data.

* `save_links_and_regions_to_csv(data, filename)`:
  * Saves the extracted links and regions to a CSV file.

* `scrape_all_links(url)`:
  * Main function that coordinates the scraping process.

#### Usage

Run the script to scrape customer story links and regions:

```bash
python genesys_company_link_scraper.py
```

This will save the data in `Data/company_links.csv`.

### 2. genesys_company_data_scraper.py

This script extracts detailed company data from the links scraped in the previous step.

#### Key Functions

* `read_input_csv(file_path)`: 
  * Reads the input CSV containing company URLs and regions.

* `initialize_details(url, region)`: 
  * Initializes a dictionary to store extracted details.

* `get_soup(url)`: 
  * Creates a BeautifulSoup object with a rotating user-agent.

* `extract_sidebar_info(soup, details)`: 
  * Extracts fields such as company name, industry, and location from the sidebar.

* `extract_partners(soup)`: 
  * Extracts partner information.

* `extract_quote(soup)`: 
  * Extracts the quote and speaker.

* `append_to_csv(data, output_path, first_write)`: 
  * Appends extracted data to a CSV.

* `process_urls(df, output_path)`: 
  * Processes URLs and saves data.

* `main()`: 
  * Orchestrates the scraping process.

#### Usage

Run the script to scrape detailed company data:

```bash
python genesys_company_data_scraper.py
```

This will save the data in `Data/company_data.csv`.

### 3. genesys_company_data_cleaning.ipynb

This Jupyter Notebook processes and cleans the scraped company data.

#### Key Functions

Splitting person_quoted field:
* Extracts person name and role from a string containing name, role, and company.

```python
# Apply the function to create new columns
df[['Person Name', 'Role in Company']] = df['person_quoted'].apply(split_person_quoted)
```

## CSV Files

### company_links.csv

Contains links and regions for customer stories.

* `index_number`: Row number
* `company_url`: URL of the customer story
* `region`: Region of the customer

### company_data.csv

Contains detailed information about each company.

* `product_url`: URL of the customer story
* `company_name`: Name of the company
* `industry`: Industry type
* `country`: Company location
* `partners`: Associated partners
* `person_quoted`: Quoted person 
* `role`  : Role of the quoted person in the company
* `region`: Region of the company

## Installation and Setup

1. Clone the repository:
```bash
git clone https://github.com/ambilynanjilath/fantacode_task
cd fantacode_task
```

2. Set up a virtual environment (optional):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

4. Run the scripts:
* Extract links and regions: `python Code/genesys_company_link_scraper.py`
* Extract detailed data: `python Code/genesys_company_data_scraper.py`

## Dependencies

* playwright
* pandas
* beautifulsoup4
* requests

Install dependencies via:
```bash
pip install playwright pandas beautifulsoup4 requests
```

Ensure Playwright browsers are installed:
```bash
playwright install
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.


## Author

Ambily Biju