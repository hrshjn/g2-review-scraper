# G2 Review Scraper

A Python-based tool to scrape reviews from G2.com for any product/company. This tool uses Google's Gemini AI to extract structured data from G2 review pages.

## Features

- Scrape reviews from any G2.com product page
- Extract structured data including ratings, pros, cons, and reviewer information
- Export results to CSV
- Support for batch processing multiple pages
- REST API for integration with other applications

## Requirements

- Python 3.8+
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/g2-review-scraper.git
cd g2-review-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
   - Get an API key from [Google AI Studio](https://ai.google.dev/)
   - Replace the `GOOGLE_API_KEY` value in the code with your API key

## Usage

### Jupyter Notebook

1. Open the Jupyter notebook:
```bash
jupyter notebook "Scrape G2 Data For Company.ipynb"
```

2. Set the `COMPANY_NAME` and `TOTAL_PAGES` variables:
```python
COMPANY_NAME = 'company-name-from-g2-url'  # Example: 'madcap-flare'
TOTAL_PAGES = 43  # Number of review pages to scrape
```

3. Run all cells to start the scraping process

### API Server

1. Start the Flask server:
```bash
python api.py
```

2. Make a POST request to `/api/scrape` with a JSON body containing the G2 URL:
```json
{
  "g2_url": "https://www.g2.com/products/company-name/reviews"
}
```

## How It Works

1. The scraper fetches HTML from G2.com for specified company and page
2. The Gemini AI model extracts structured data from the HTML
3. The data is processed and saved as CSV
4. Failed pages are tracked for retry

## Security Considerations

- The API key included in this code should be replaced with your own
- Consider using environment variables for API keys in production
- The scraper uses headers to mimic a browser - be aware of G2's terms of service

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 