#!/usr/bin/env python3
import os
import time
import json
import argparse

import google.generativeai as genai
import pandas as pd
import requests

def get_html_for_company(company_name, page_no):
    """Get HTML content for a specific company page"""
    url = f"https://www.g2.com/products/{company_name}/reviews?page={page_no}&source=search&_pjax=%23pjax-container"
    payload = {}
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
      'Accept': 'text/html, */*; q=0.01',
      'Sec-Fetch-Site': 'same-origin',
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Sec-Fetch-Mode': 'cors',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0.1 Safari/605.1.15',
      'Referer': 'https://www.g2.com/products/heap-by-contentsquare/reviews',
      'Sec-Fetch-Dest': 'empty',
      'X-PJAX-Container': '#pjax-container',
      'X-Requested-With': 'XMLHttpRequest',
      'Priority': 'u=3, i',
      'X-PJAX': 'true',
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()

def scrape_g2_reviews(company_name, total_pages, api_key, output_file=None):
    """
    Scrape G2 reviews for a specific company
    
    Args:
        company_name (str): Name of the company as it appears in G2 URL
        total_pages (int): Number of pages to scrape
        api_key (str): Google Gemini API key
        output_file (str, optional): Output CSV filename. Defaults to company_name_reviews.csv
    
    Returns:
        list: List of processed reviews
    """
    if not output_file:
        output_file = f"{company_name}_reviews.csv"
        
    processed_pages = []
    failed_pages = []
    processed_reviews = []

    genai.configure(api_key=api_key)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config,
    )

    for page_no in range(1, total_pages + 1):
        if page_no in processed_pages:
            print(f"Skipped Page No {page_no}")
            continue

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        f"""
                        From the div below can you get all the g2 reviews from this html in this format

                        {{
                            "review_date": "2024-07-09",
                            "reviewer_name": "Mark K.",
                            "reviewer_job_title": "Executive Director in Engineering",
                            "reviewer_company_size": "Enterprise (> 1000 emp.)",
                            "review_rating": 5.0,
                            "review_title": "Autocapture is awesome",
                            "review_pros": "Heap Analytics' autocapture and post-capture event definition combine to enable us to capture everything up-front and to only making the investment to categorize user events that are actually business-significant. This lets us defer investment or even eliminate investment in defining events. It also enables us to avoid the expense of having valuable developer time taken up inserting event capture code throughout the front-end codebase.\\n\\nThe business value of putting the event definitions and taxonomy in the hands of both our Product Manager and Customer Experience Managers has revolutionized the User Analytics and Product Analytics functions in our company. The value of the freed-up opportunity cost to engineering is multiplicative because it really lets engineering focus on development of customer features instead of being distracted by the cross-cutting concerns of implementing user analytics and in particular of implementing taxonomized product analytics.",
                            "review_cons": "The graphical and data analysis features that come out-of-the-box are fine, but not fancy. We also bought Heap Connect so we do have the capability to define arbitrarily complex queries and visualization on Heap data, but it would be nice to have better capabilities out-of-the-box.",
                            "review_problems_solved": "We use Heap to:\\n\\n1. Measure and track customer engagement for our business-to-business web applications.\\n\\n2. We use these engagement measures to identify issues in upcoming annual renewal processes and ongoing customer engagement.\\n\\n3. Measure and analyze the success of new product features and identify areas for improvement in our existing features.",
                            "review_url": "https://www.g2.com/products/heap-by-contentsquare/reviews/heap-by-contentsquare-review-9874230"
                        }}

                        {get_html_for_company(company_name, page_no)}
                        """
                    ],
                }
            ]
        )
        
        response = chat_session.send_message("INSERT_INPUT_HERE")

        try:
            reviews_data = json.loads(response.text.replace('```json', '').replace('```',''))
            processed_reviews.extend(reviews_data)
            processed_pages.append(page_no)
            print(f"Page no: {page_no} done")
        except Exception as e:
            print(f"Exception {e}")
            print(f"Failed Page no: {page_no} done")
            failed_pages.append(page_no)
            continue

    # Save to CSV
    pd.DataFrame(processed_reviews).to_csv(output_file, index=False)
    print(f"Saved {len(processed_reviews)} reviews to {output_file}")
    
    if failed_pages:
        print(f"Failed pages: {failed_pages}")
        
    return processed_reviews

def main():
    parser = argparse.ArgumentParser(description='Scrape G2 reviews for a company')
    parser.add_argument('company_name', type=str, help='Company name as it appears in G2 URL')
    parser.add_argument('--pages', type=int, default=10, help='Number of pages to scrape (default: 10)')
    parser.add_argument('--api-key', type=str, help='Google Gemini API key')
    parser.add_argument('--output', type=str, help='Output CSV filename')
    
    args = parser.parse_args()
    
    api_key = args.api_key
    if not api_key:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            parser.error("API key must be provided either as argument or as GEMINI_API_KEY environment variable")
    
    scrape_g2_reviews(
        company_name=args.company_name,
        total_pages=args.pages,
        api_key=api_key,
        output_file=args.output
    )

if __name__ == "__main__":
    main() 