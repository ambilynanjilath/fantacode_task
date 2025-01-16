import csv
from playwright.sync_api import sync_playwright

# URL to scrape
url = "https://www.genesys.com/customer-stories"

def select_genesys_cloud_filters(page):
    """Selects the Genesys Cloud and Genesys Cloud EX filter checkboxes by expanding the accordion and clicking the checkboxes."""
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
                checkbox_genesys = nested_element.locator("input[type='checkbox']#genesys\\+cloud")
                if checkbox_genesys.count() > 0:
                    checkbox_genesys.check()
                    print("'Genesys Cloud' checkbox selected")
                else:
                    print("'Genesys Cloud' checkbox not found")
                
                # Click 'Genesys Cloud EX' checkbox
                checkbox_genesys_ex = nested_element.locator("input[type='checkbox']#genesys\\+cloud\\+ex")
                if checkbox_genesys_ex.count() > 0:
                    checkbox_genesys_ex.check()
                    print("'Genesys Cloud EX' checkbox selected")
                else:
                    print("'Genesys Cloud EX' checkbox not found")

                page.wait_for_timeout(20000)  # Wait for 20 seconds after checking the checkboxes
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
    """Scrolls to the bottom and scrapes filtered customer story links along with regions from the page."""
    try:
        product_data = []

        # Scroll to the bottom of the page
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
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

                if link:
                    product_data.append((link, region))

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
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
    """Saves the list of links and regions to a CSV file with the specified format."""
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
    """Main function to scrape all the customer story links and regions from the provided URL."""
    try:
        all_product_data = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)

            if select_genesys_cloud_filters(page):
                all_product_data.extend(scrape_customer_story_links_and_regions(page))
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
