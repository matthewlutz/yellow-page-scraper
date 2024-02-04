'''
Author: Matthew Lutz
Date: 2/02/2024
Description: This script scrapes the Yellow Pages website for restaurants in a given location that do not have a website. 
To run the script, pass the location as a command-line argument. The script will save the results to a CSV file in the same directory as this file. 
For example run 'python yellow-scraper.py "Chicago, IL"'. This will return a list of restaurants in Chicago that do not have a website.
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import csv
import sys

def fetch_page(url):
    """Fetch a page and return its BeautifulSoup object."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for bad status codes
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

def parse_restaurants(soup):
    """Parse the BeautifulSoup object for restaurant data."""
    restaurants = []
    restaurant_list = soup.find_all("div", class_="info")
    for restaurant_info in restaurant_list:
        restaurant_name = restaurant_info.find("a", class_="business-name").text.strip()
        website_link = restaurant_info.find("a", class_="track-visit-website")
        phone_element = restaurant_info.find("div", class_="phones")
        phone_number = phone_element.text.strip() if phone_element else "No phone number available"
        if not website_link:
            restaurants.append((restaurant_name, phone_number))
    return restaurants

def get_next_page_url(soup, base_url):
    """Determine the URL of the next page."""
    next_button = soup.find("a", class_="next")
    if next_button and next_button.get("href"):
        return urljoin(base_url, next_button.get("href"))
    return None

def scrape_yellow_pages(location):
    base_url = "https://www.yellowpages.com"
    search_url = f"{base_url}/search?search_terms=restaurants&geo_location_terms={quote_plus(location)}"
    
    all_restaurants = []

    while search_url:
        soup = fetch_page(search_url)
        restaurants = parse_restaurants(soup)
        all_restaurants.extend(restaurants)
        search_url = get_next_page_url(soup, base_url)

    return all_restaurants

def save_to_csv(data, filename):
    """Save the list of restaurants to a CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Restaurant Name", "Phone Number"])
        for name, phone in data:
            writer.writerow([name, phone])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        location = sys.argv[1]
    else:
        print("Usage: python script_name.py 'Location'")
        sys.exit(1)

    results = scrape_yellow_pages(location)
    output_filename = f"restaurants_without_websites_{quote_plus(location)}.csv"
    save_to_csv(results, output_filename)
    print(f"Saved results to {output_filename}")
