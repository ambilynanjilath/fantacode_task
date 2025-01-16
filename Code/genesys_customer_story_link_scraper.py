import csv
from playwright.sync_api import sync_playwright

# URL to scrape
url = "https://www.genesys.com/customer-stories"

def select_genesys_cloud_filter(page):
    """Selects the Genesys Cloud filter checkbox by expanding the accordion and clicking the checkbox."""
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

                checkbox = nested_element.locator("input[type='checkbox']#genesys\\+cloud")
                if checkbox.count() > 0:
                    checkbox.check()
                    page.wait_for_timeout(20000)  # Wait for 20 seconds after checking the checkbox
                    print("'Genesys Cloud' checkbox selected")
                    return True
                else:
                    print("'Genesys Cloud' checkbox not found")
            else:
                print("Products filter section not found")
        else:
            print("Main accordion not found")
        return False
    except Exception as e:
        print(f"Error in selecting Genesys Cloud filter: {e}")
        return False


def scrape_customer_story_links(page):
    """Scrolls to the bottom and scrapes filtered customer story links from the page."""
    try:
        product_links = set()

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

        # Scroll again and extract non-filtered links
        while True:
            story_cards = page.query_selector_all(
                "div.row.gutter-small div.grid-item.card-col:not(.filtered-item)"
            )
            for card in story_cards:
                link_element = card.query_selector("a.card.component")
                if link_element:
                    link = link_element.get_attribute("href")
                    if link:
                        product_links.add(link)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            is_end_of_page = page.evaluate(
                "window.scrollY + window.innerHeight >= document.body.scrollHeight"
            )
            if is_end_of_page:
                break

        return sorted(product_links)
    except Exception as e:
        print(f"Error while scraping customer story links: {e}")
        return []


def save_links_to_csv(links, filename="Data/customer_story_links.csv"):
    """Saves the list of links to a CSV file with the specified format."""
    try:
        unique_links = list(set(links))
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["index_number", "company_url"])
            for idx, link in enumerate(unique_links, start=1):
                writer.writerow([idx, link])
        print(f"Links saved to {filename}")
    except Exception as e:
        print(f"Error saving links to CSV: {e}")


def scrape_all_links(url):
    """Main function to scrape all the customer story links from the provided URL."""
    try:
        all_product_links = set()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url)

            if select_genesys_cloud_filter(page):
                all_product_links.update(scrape_customer_story_links(page))
            else:
                print("Failed to apply Genesys Cloud filter")

            browser.close()
        
        return sorted(all_product_links)
    except Exception as e:
        print(f"Error during the scraping process: {e}")
        return []


# Execute the scraping
all_links = scrape_all_links(url)
if all_links:
    save_links_to_csv(all_links)
else:
    print("No links found. Scraping failed.")
