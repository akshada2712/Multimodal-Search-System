import os
import time
import random
import json
import pandas as pd
from datetime import datetime
import logging
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

# Simplified folder structure
BASE_DIR = "Renesas_Scraper"
for folder in ["images", "data", "logs"]:
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "logs", f"scraping_{datetime.now().strftime('%Y%m%d_%H%M')}.log")),
        logging.StreamHandler()
    ]
)

def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters and replacing spaces with underscores"""
    logging.debug(f"Sanitizing filename: {filename}")
    # Remove invalid characters and replace spaces/slashes with underscores
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace(' ', '_')
    filename = filename.replace('/', '_')
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    result = filename.lower()
    logging.debug(f"Sanitized filename: {result}")
    return result

def get_soup(url):
    """Simplified soup object getter"""
    logging.info(f"Fetching page: {url}")
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        wait_time = random.uniform(2, 4)
        logging.debug(f"Waiting {wait_time:.2f} seconds")
        time.sleep(wait_time)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        logging.info(f"Successfully fetched page: {url}")
        return soup
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def get_winning_applications():
    """Get main applications"""
    logging.info("Starting to fetch main applications")
    soup = get_soup("https://www.renesas.com/en/applications")
    if not soup:
        logging.error("Failed to get main applications page")
        return {}
    
    applications = {
        category.select_one(".rcard__title").text.strip(): 
        "https://www.renesas.com" + category.select_one(".rcard__title").get("href")
        for category in soup.select(".rcard")
        if category.select_one(".rcard__title")
    }
    
    logging.info(f"Found {len(applications)} main applications")
    for app, url in applications.items():
        logging.debug(f"Application found: {app} -> {url}")
    return applications

def get_sub_application_categories(url):
    """Get sub-categories"""
    logging.info(f"Fetching sub-applications from: {url}")
    soup = get_soup(url)
    if not soup:
        logging.error(f"Failed to get sub-applications from: {url}")
        return {}
    
    categories = {
        category.select_one(".rcard__title").text.strip(): 
        "https://www.renesas.com" + category.select_one(".rcard__title").get("href")
        for category in soup.select(".rcard")
        if category.select_one(".rcard__title")
    }
    
    logging.info(f"Found {len(categories)} sub-applications")
    for cat, cat_url in categories.items():
        logging.debug(f"Sub-application found: {cat} -> {cat_url}")
    return categories

def extract_categories(url):
    """Extract category and subcategory data"""
    logging.info(f"Extracting categories from: {url}")
    soup = get_soup(url)
    if not soup:
        logging.error(f"Failed to get categories from: {url}")
        return {}
    
    categories = {}
    for category in soup.find_all("div", class_="application-category-list__group"):
        cat_name = category.find("h3").text.strip()
        logging.debug(f"Processing category: {cat_name}")
        subcategories = []
        
        for item in category.find_all("li"):
            if link := item.find("a"):
                subcat = {
                    "name": link.text.strip(),
                    "url": "https://www.renesas.com" + link["href"]
                }
                subcategories.append(subcat)
                logging.debug(f"Found subcategory: {subcat['name']} -> {subcat['url']}")
        
        if subcategories:
            categories[cat_name] = subcategories
            logging.info(f"Category '{cat_name}' has {len(subcategories)} subcategories")
            
    return categories

def extract_data(url, app_name, sub_app_name, category_name, subcat_name):
    """Extract final level data"""
    logging.info(f"Extracting data for {subcat_name} under {app_name}/{sub_app_name}/{category_name}")
    soup = get_soup(url)
    if not soup:
        logging.error(f"Failed to get data from: {url}")
        return None
    
    # Get description
    desc_section = soup.find("section", id="tab-description")
    description = desc_section.find("div", class_="wysiwyg").text.strip() if desc_section else ""
    logging.debug(f"Description length: {len(description)} characters")
    
    # Get applications list
    app_section = soup.find("section", id="tab-applications")
    applications = [li.text.strip() for li in (app_section.find_all("li") if app_section else [])]
    logging.debug(f"Found {len(applications)} applications")
    
    # Handle SVG
    svg_filename = ""
    if div_tag := soup.find("div", class_="diagram-section-media"):
        if svg_tag := div_tag.find("svg"):
            logging.info("Found SVG diagram, processing...")
            try:
                base_filename = f"{sanitize_filename(app_name)}_{sanitize_filename(sub_app_name)}_{sanitize_filename(subcat_name)}"
                svg_filename = f"{base_filename}.svg"
                filepath = os.path.join(BASE_DIR, "images", svg_filename)
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(str(svg_tag))
                logging.info(f"Successfully saved SVG to: {filepath}")
            except Exception as e:
                logging.error(f"Failed to save SVG file: {str(e)}")
                svg_filename = ""
    
    data = {
        "application": app_name,
        "sub_application": sub_app_name,
        "category": category_name,
        "subcategory": subcat_name,
        "description": description,
        "applications": applications,
        "image": svg_filename
    }
    logging.debug(f"Extracted data: {json.dumps(data, indent=2)}")
    return data

def main():
    logging.info("Starting scraping process")
    start_time = time.time()
    all_data = []
    
    try:
        # Level 1: Main applications
        applications = get_winning_applications()
        logging.info(f"Found {len(applications)} main applications")
        
        
        # Process all levels
        for app_name, app_url in tqdm(applications.items(), desc="Processing applications"):
            app_data = []
            logging.info(f"Processing main application: {app_name}")
            
            sub_apps = get_sub_application_categories(app_url)
            logging.info(f"Found {len(sub_apps)} sub-applications for {app_name}")
            
            for sub_app_name, sub_app_url in tqdm(sub_apps.items(), desc=f"Processing {app_name}"):
                logging.info(f"Processing sub-application: {sub_app_name}")
                
                categories = extract_categories(sub_app_url)
                total_subcats = sum(len(subcats) for subcats in categories.values())
                logging.info(f"Found {len(categories)} categories with {total_subcats} total subcategories")
                
                for cat_name, subcats in categories.items():
                    logging.info(f"Processing category: {cat_name}")
                    
                    for subcat in subcats:
                        logging.info(f"Processing subcategory: {subcat['name']}")
                        data = extract_data(
                            subcat["url"], 
                            app_name,
                            sub_app_name,
                            cat_name,
                            subcat["name"]
                        )
                        if data:
                            all_data.append(data)
                            app_data.append(data)
                            logging.debug("Data successfully extracted and added")
                        
                        wait_time = random.uniform(1, 3)
                        logging.debug(f"Waiting {wait_time:.2f} seconds before next request")
                        time.sleep(wait_time)
            
            logging.info(f"Saving {len(app_data)} records to CSV")
            csv_path = os.path.join(BASE_DIR, "data", f"{app_name}.csv")
            pd.DataFrame(app_data).to_csv(csv_path, index=False)

            logging.info(f"Data saved to CSV: {csv_path}")
        
        # Save final data
        logging.info(f"Saving {len(all_data)} records to CSV and JSON")
        csv_path = os.path.join(BASE_DIR, "data", "complete_data.csv")
        json_path = os.path.join(BASE_DIR, "data", "raw_data.json")
        
        pd.DataFrame(all_data).to_csv(csv_path, index=False)
        logging.info(f"Data saved to CSV: {csv_path}")
        
        with open(json_path, "w") as f:
            json.dump(all_data, f, indent=2)
        logging.info(f"Data saved to JSON: {json_path}")
        
        end_time = time.time()
        duration = end_time - start_time
        logging.info(f"Scraping completed in {duration:.2f} seconds")
        
    except Exception as e:
        logging.error(f"Critical error during scraping: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()