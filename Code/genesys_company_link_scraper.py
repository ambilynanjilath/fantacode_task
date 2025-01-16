import csv
from playwright.sync_api import sync_playwright

# URL to scrape
url = "https://www.genesys.com/customer-stories"

def select_genesys_cloud_filters(page):
    """
    Selects the 'Genesys Cloud' and 'Genesys Cloud EX' filter checkboxes on the 
    provided page.

    This function first locates the main filter accordion and expands it if it's 
    collapsed. Then, it selects the 'Genesys Cloud' and 'Genesys Cloud EX' 
    checkboxes if they are present. A delay of 20 seconds is introduced after 
    checking the checkboxes to ensure the page has enough time to update.

    Args:
        page: A Playwright page object representing the page to interact with.

    Returns:
        bool: True if the checkboxes were successfully selected, False otherwise.
    """
    try:
        element = page.locator("div.accordion#cs-filter")
        
        if element.count() > 0:
            print("Found main accordion")
            nested_element = element.locator(
                "div#tax_products_programs.check-group.accordion-item"
            )
            if nested_element.count() > 0:
                print("Found products filter section")
                button = nested_element.locator("button.accordion-button")
                aria_expanded = button.get_attribute("aria-expanded")

                if aria_expanded == "false":
                    button.click()
                    page.wait_for_timeout(1000)

                # Click 'Genesys Cloud' checkbox
                checkbox_genesys = nested_element.locator(
                    "input[type='checkbox']#genesys\\+cloud"
                )
                if checkbox_genesys.count() > 0:
                    checkbox_genesys.check()
                    print("'Genesys Cloud' checkbox selected")
                else:
                    print("'Genesys Cloud' checkbox not found")
                
                # Click 'Genesys Cloud EX' checkbox
                checkbox_genesys_ex = nested_element.locator(
                    "input[type='checkbox']#genesys\\+cloud\\+ex"
                )
                if checkbox_genesys_ex.count() > 0:
                    checkbox_genesys_ex.check()
                    print("'Genesys Cloud EX' checkbox selected")
                else:
                    print("'Genesys Cloud EX' checkbox not found")

                page.wait_for_timeout(20000)  # Wait for 20 seconds 
                                               #after checking the checkboxes
                return True
            else:
                print("Products filter section not found")
        else:
            print("Main accordion not found")
        
        return False
    except Exception as e:
        print(f"Error in selecting Genesys Cloud filters: {e}")
        return False


def scrape_customer_story_links_and_regions(page):
    """
    Scrolls through the page and extracts customer story links along 
    with their associated regions.

    This function performs infinite scrolling until the end of the page 
    is reached, collects the customer story links, and extracts the 
    region information associated with each story.

    Args:
        page: A Playwright page object representing the page to scrape.

    Returns:
        list: A list of tuples where each tuple contains a customer 
              story link and its associated region.
              Example: [("https://link1.com", "NA"), 
                        ("https://link2.com", "EMEA")]
    """
    try:
        product_data = []

        # Scroll to the bottom of the page
        while True:
            page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            page.wait_for_timeout(2000)  # Wait for content to load after scrolling
            is_end_of_page = page.evaluate(
                "window.scrollY + window.innerHeight >= document.body.scrollHeight"
            )
            if is_end_of_page:
                break

        # Scroll back to the top
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(2000)

        # Scroll again and extract non-filtered links and region data
        while True:
            story_cards = page.query_selector_all(
                "div.row.gutter-small div.grid-item.card-col:not(.filtered-item)"
            )
            for card in story_cards:
                link_element = card.query_selector("a.card.component")
                region_element = card.query_selector("p.cs-region.assettag.mb-0")
                
                link = link_element.get_attribute("href") if link_element else None
                region = region_element.inner_text().strip() if region_element else "Unknown"
                
                # Check if the region is "NA" and return "NA"
                if region == "NA":
                    region = "NA"

                if link:
                    product_data.append((link, region))

            page.evaluate(
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            page.wait_for_timeout(2000)
            is_end_of_page = page.evaluate(
                "window.scrollY + window.innerHeight >= document.body.scrollHeight"
            )
            if is_end_of_page:
                break

        return product_data
    except Exception as e:
        print(f"Error while scraping customer story links and regions: {e}")
        return []

def save_links_and_regions_to_csv(data, filename="Data/company_links.csv"):
    """
    Saves the customer story links and regions to a CSV file with an index.

    This function takes a list of tuples containing customer story links 
    and their associated regions, removes duplicate entries, and saves 
    the data to a CSV file. The CSV file contains columns for the index 
    number, company URL, and region.

    Args:
        data (list): A list of tuples where each tuple contains a customer 
                     story link and its region.
                     Example: [("https://link1.com", "North America"), 
                               ("https://link2.com", "EMEA")]
        filename (str): The name of the CSV file to save the data to. 
                        Defaults to "Data/company_links.csv".

    Returns:
        None
    """
    try:
        unique_data = list(set(data))
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["index_number", "company_url", "region"])
            for idx, (link, region) in enumerate(unique_data, start=1):
                writer.writerow([idx, link, region])
        print(f"Links and regions saved to {filename}")
    except Exception as e:
        print(f"Error saving links and regions to CSV: {e}")

def scrape_all_links(url):
    """
    Scrapes all customer story links and their associated regions from the provided URL.

    This function initializes a Playwright browser instance, navigates to the provided URL, 
    applies the Genesys Cloud filter, and extracts customer story links and regions. The 
    results are returned as a list of tuples containing the link and region data. 

    Args:
        url (str): The URL of the page to scrape customer story links and regions from.

    Returns:
        list: A list of tuples where each tuple contains a customer story link 
              and its associated region.
              Example:
                [("https://link1.com", "North America"), 
                 ("https://link2.com", "EMEA")]
    """
    try:
        all_product_data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)

            if select_genesys_cloud_filters(page):
                all_product_data.extend(
                    scrape_customer_story_links_and_regions(page)
                )
            else:
                print("Failed to apply Genesys Cloud filter")

            browser.close()

        return all_product_data
    except Exception as e:
        print(f"Error during the scraping process: {e}")
        return []


# Execute the scraping
all_data = scrape_all_links(url)
if all_data:
    save_links_and_regions_to_csv(all_data)
else:
    print("No data found. Scraping failed.")
