# import csv
# from playwright.sync_api import sync_playwright

# # URL to scrape
# url = "https://www.genesys.com/customer-stories"


# def scrape_customer_story_links(page):
#     """Scrapes customer story links from the page."""
#     product_links = []
    
#     story_cards = page.query_selector_all(
#         "div.row.gutter-small div.grid-item.card-col a.card.component"
#     )
    
#     for card in story_cards:
#         link = card.get_attribute("href")
        
#         if link:
#             product_links.append(link)
    
#     return product_links


# def load_more_content(page):
#     """Clicks the 'Load More' button if present and waits for content to load."""
#     try:
#         load_more_button = page.query_selector(
#             ".load-more-container .load-more-btn"
#         )
        
#         if load_more_button and load_more_button.is_visible():
#             load_more_button.click()
            
#             page.wait_for_timeout(2000)  # Wait to allow content to load
#             return True
#     except Exception as e:
#         print(f"Error while loading more content: {e}")
    
#     return False


# def save_links_to_csv(links, filename="Data/customer_story_links.csv"):
#     """Saves the list of links to a CSV file with the specified format."""
#     with open(filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
        
#         writer.writerow(["index_number", "company_url"])  # Writing the header
        
#         for idx, link in enumerate(links, start=1):
#             writer.writerow([idx, link])


# def scrape_all_links(url):
#     """Main function to scrape all the customer story links from the provided URL."""
#     all_product_links = set()  # Use a set to avoid duplicate links
    
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)  # Set headless=True to run without GUI
#         page = browser.new_page()
        
#         page.goto(url)

#         # Scrape initial set of links
#         all_product_links.update(
#             scrape_customer_story_links(page)
#         )

#         while load_more_content(page):
#             all_product_links.update(
#                 scrape_customer_story_links(page)
#             )

#         browser.close()
    
#     return sorted(all_product_links)  # Return sorted list of links


# # Scrape all links and save them to CSV
# all_links = scrape_all_links(url)

# save_links_to_csv(all_links)

# print("Scraping complete. The links have been saved to 'customer_story_links.csv'.")



import csv
from playwright.sync_api import sync_playwright

# URL to scrape
url = "https://www.genesys.com/customer-stories"


def scrape_customer_story_links(page):
    """Scrapes customer story links from the page."""
    product_links = []
    
    story_cards = page.query_selector_all(
        "div.row.gutter-small div.grid-item.card-col a.card.component"
    )
    
    for card in story_cards:
        link = card.get_attribute("href")
        
        if link:
            product_links.append(link)
    
    return product_links


def load_more_content(page):
    """Clicks the 'Load More' button if present and waits for content to load."""
    try:
        load_more_button = page.query_selector(
            ".load-more-container .load-more-btn"
        )
        
        if load_more_button and load_more_button.is_visible():
            load_more_button.click()
            
            page.wait_for_timeout(2000)  # Wait to allow content to load
            return True
    except Exception as e:
        print(f"Error while loading more content: {e}")
    
    return False


def save_links_to_csv(links, filename="Data/customer_story_links.csv"):
    """Saves the list of links to a CSV file with the specified format."""
    # Remove duplicates by converting the list to a set and back to a list
    unique_links = list(set(links))
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(["index_number", "company_url"])  # Writing the header
        
        for idx, link in enumerate(unique_links, start=1):
            writer.writerow([idx, link])


def scrape_all_links(url):
    """Main function to scrape all the customer story links from the provided URL."""
    all_product_links = set()  # Use a set to avoid duplicate links
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=True to run without GUI
        page = browser.new_page()
        
        page.goto(url)

        # Scrape initial set of links
        all_product_links.update(
            scrape_customer_story_links(page)
        )

        while load_more_content(page):
            all_product_links.update(
                scrape_customer_story_links(page)
            )

        browser.close()
    
    return sorted(all_product_links)  # Return sorted list of links


# Scrape all links and save them to CSV
all_links = scrape_all_links(url)

save_links_to_csv(all_links)

print("Scraping complete. The links have been saved to 'customer_story_links.csv'.")
