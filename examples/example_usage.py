#!/usr/bin/env python3
"""
Example usage of G2 Review Scraper
"""
import os
import sys

# Add parent directory to path to import scraper module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import scrape_g2_reviews

# Replace with your actual API key
API_KEY = "your-api-key-here"
# Or use environment variable
# API_KEY = os.environ.get("GEMINI_API_KEY")

# Company to scrape (from G2 URL)
COMPANY_NAME = "slack"

# Number of pages to scrape
TOTAL_PAGES = 3

def main():
    """Run example scraper"""
    print(f"Scraping G2 reviews for {COMPANY_NAME}...")
    
    reviews = scrape_g2_reviews(
        company_name=COMPANY_NAME,
        total_pages=TOTAL_PAGES,
        api_key=API_KEY,
        output_file=f"example_{COMPANY_NAME}_reviews.csv"
    )
    
    print(f"Total reviews scraped: {len(reviews)}")
    print("Example of a review:")
    if reviews:
        for key, value in reviews[0].items():
            if key in ["review_title", "reviewer_name", "review_rating"]:
                print(f"{key}: {value}")
    
    print(f"Full data saved to example_{COMPANY_NAME}_reviews.csv")

if __name__ == "__main__":
    main() 