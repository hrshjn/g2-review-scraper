from flask import Flask, request, send_file, jsonify
import re
import os
import time
import json
import pandas as pd
import requests
import google.generativeai as genai
from io import StringIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GOOGLE_API_KEY = 'AIzaSyCSuF2qsrfXAre-wP5Nmj9VZSHxfAv64mA'
TOTAL_PAGES = 100

def extract_company_name(g2_url):
    """Extract company name from G2 URL"""
    match = re.search(r'/products/([^/]+)/', g2_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid G2 URL format")

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
      'Cookie': '_sp_id.6c8b=f8918d80-d364-4fb3-a063-d8c35bc642a1.1737973804.1.1737973895..b3cd27b4-a129-44bb-8e19-1eb661da9e9b..95f31be0-1a47-49ba-b241-2783aa2afcb7.1737973803862.17; _sp_ses.6c8b=*; _ga_MFZ5NDXZ5F=GS1.1.1737973804.1.0.1737973873.60.0.0; sp=cafa8012-4c90-431c-a4dc-09d48fae889e; _gat=1; zfm_usr_sess_ck_id=bbh6c8ti381737973804831; AWSALB=hGpctbneqaODhehpUyjeMkQrqWXxe4Mrb8/zsc4Yl5ZthYgsThg2Y2IWSBqBYSrNuenedu3tXOiQFlifuU1jOLxUIh21/8GuOs6qnfP7nN+siliW05Sf6Rrq0B4+; AWSALBCORS=hGpctbneqaODhehpUyjeMkQrqWXxe4Mrb8/zsc4Yl5ZthYgsThg2Y2IWSBqBYSrNuenedu3tXOiQFlifuU1jOLxUIh21/8GuOs6qnfP7nN+siliW05Sf6Rrq0B4+; amplitude_session=1737973801573; datadome=rG55RDHcRVXCh2AoGCSvPnVmpYPn2eYzBtHUJZxQzpXUa1o_xD9pRQGfuWtturTLZ8NfOyTiJtMtcTZ2PpPoBtt7EDPd0rzbeZ27fpqw82wKkj1BMCPDgQJE0HGGX4zk; __ar_v4=%7CC6MKFN32KVBHZAS4DKYVVW%3A20250126%3A1%7CEEPCTRZ5RNC6ZCBB2PJM4J%3A20250126%3A1%7CNBMTYK27EJFT3GYAV7FM56%3A20250126%3A1; __adroll_fpc=b52915217daf33df00592c9e58c1add4-1737973807788; _fbp=fb.1.1737973807750.199879638384025595; g_state={\"i_p\":1737981007915,\"i_l\":1}; _ga=GA1.2.53959668.1737973804; _gid=GA1.2.1703947697.1737973805; zfm_app_3SDj9c=show; zfm_app_9f3XVc=show; zfm_app_S3V5ee=show; zfm_app_u1h4JN=show; _gcl_au=1.1.1416334449.1737973804; osano_consentmanager=qtFNYneNtGMxnQYwhitmSwIBFWA79McXC1eWolsT8aVkK_6Ey-eY0_qotjgYEHgBXekXpBII0w9EEbe5MOo8UU9rKmQIquWL46nkAqi7w5GQjGGxEB3odkn3Zdx5iP4-GyqprtQU571yVqu7r2bTlprh0dqm0PXrz8fSgD9qLfnfhdorgz3bMz__LOmSpqD_EcOpkBHnURKVDXFXz_rTIWrLPl95DDudKbGe5u8OWu9q6RdqUpIfxnzHfeCYb4iHv87Mv_zY2WE4qUGCWKYfS7vdrBjFDEQj_IjQqeHBNbV52G-A9LEEVPj8PTFzWDeswCB9Sw-JZfU=; osano_consentmanager_uuid=6021956d-ef4c-456d-8a68-754fbfda4bb6; zfm_cnt_ck_id=g73lzrcl2z81737973804834; _g2_session_id=6e007c3f28e93b771a714795788b606d; events_distinct_id=4d57b90a-d430-4e0b-9db2-c172202bed7a; __cf_bm=KBSU9Mg7VSzT1opkSGrZA2nZX_tHsry3YTLF6ctu_OA-1737973800-1.0.1.1-yAHtdIcf5Q1iuPVpGVAfAhNsTqBUmpWGjdAv1Iz_cnlmESoQEyNWwwJM5cJYBoJl5XN._B0Kdx5ShgvQwBfB5A; cf_clearance=kXE0NFWuVh_NYv3E44WvJFwWHsWqlIsrGhrL4i99jRg-1737973800-1.2.1.1-3jV3XfL1UZEakkx66A3UpmBczerNgbNPi4Q2ewLtWv70KcpdDVeXxrMZOmE2WMZEMAVpsoCFpzNN9kXUrw0KXmbQ3OtOp1sKZbu9HYXndXYUo4UzDZ6fiuU4nzDD5lUp3V8LTozAZrhw0tY9sPTncwqlJcIKFCaxfBhYMGuygqDn3c8QjzNb.qEIxuimBeV4F4f0wvYFztaGU19n5fcvkaL.daJtpDHIBsAwXa62ea_I1nwP.gOTM3NmwSaDU6I0bfZa6YlC_FWy5kK6MJ8NC5wRjVq4.bMGduR1OVU03i0; __cf_bm=alF1GvLhVgRVV1wGUzk.J.BPUC56vwrQbemnqIRo6Eo-1737974764-1.0.1.1-ytX6JKTdeHgE1CRdwKKeOaaXHfzxQiLK19USqiF.2kCRYSPaQa.UY9V_F3hwyfLH64tIXt3QZnv_z_lezwG1kw; datadome=97pkP7MIbh4wMp3YisTyX4t_E5w0rB8mIfdK4y~Ty4NfT8oJVm7dr6b8hZZ6tlwjJEGlT6lRv7FlrnB1wUYs59V92~Ih90VRZTOL~qiFlYaY3jQG6R~Z2N2TwLwjr~9_; AWSALB=PCYWpDJMizo8trgmXuB7w8QaZfU2Irhgmwkic0YF0tv4XPOELtdvsOlA5hd7SrJ9niAJ55I1ujUEuVfrs+2pVoabNya8iSVtGz8aY929/haxTIw8LTKu2H/BXw5V; AWSALBCORS=PCYWpDJMizo8trgmXuB7w8QaZfU2Irhgmwkic0YF0tv4XPOELtdvsOlA5hd7SrJ9niAJ55I1ujUEuVfrs+2pVoabNya8iSVtGz8aY929/haxTIw8LTKu2H/BXw5V; amplitude_session=1737973801573; ue-event-snowplow-bbaf7bdf-0e01-4d2c-9a52-7b3a59cb9969=W1siYWR2ZXJ0aXNlbWVudC12aWV3ZWQiLHsicHJvZHVjdF9pZCI6MTQ0NTgy%0ALCJwcm9kdWN0X3V1aWQiOiJiMTZmYTZkZS04YWZkLTQ4NmUtYTE0My03NGVh%0AYTg0NWZmZmEiLCJwcm9kdWN0IjoiSG9ja2V5U3RhY2siLCJ2ZW5kb3JfaWQi%0AOjEyNzI0OSwicHJvZHVjdF90eXBlIjoiU29mdHdhcmUiLCJhZF90eXBlIjoi%0AY2F0ZWdvcnlfY29tcGV0aXRvciIsInR5cGUiOiJBZHZlcnRpc2luZzo6UHJv%0AZHVjdEFkIiwidGFyZ2V0X3Byb2R1Y3RfaWQiOm51bGwsImNhdGVnb3JpZXMi%0AOlsiQWNjb3VudC1CYXNlZCBBbmFseXRpY3MiLCJNYXJrZXRpbmcgQW5hbHl0%0AaWNzIiwiQW5hbHl0aWNzIFBsYXRmb3JtcyIsIkNvbnRlbnQgQW5hbHl0aWNz%0AIiwiQXR0cmlidXRpb24iLCJEaWdpdGFsIEFuYWx5dGljcyIsIlJldmVudWUg%0AT3BlcmF0aW9ucyBcdTAwMjYgSW50ZWxsaWdlbmNlIChST1x1MDAyNkkpIiwi%0AQ3VzdG9tZXIgSm91cm5leSBBbmFseXRpY3MiXSwiY2F0ZWdvcnlfaWRzIjpb%0AMTAzOCw2MjQsNjIwLDYxOCwzNjcsMTEsMjY0MSwxMjI0XSwidGFnIjoiYWQu%0AY2F0ZWdvcnlfY29tcGV0aXRvci5wcm9kdWN0X3BhZ2VfaGVhZGVyIiwiYWRt%0AaW5fdmlld2VyIjpmYWxzZSwidXNlcl90eXBlIjoiZ3Vlc3QiLCJpc19wcGMi%0AOmZhbHNlfSwiYmJhZjdiZGYtMGUwMS00ZDJjLTlhNTItN2IzYTU5Y2I5OTY5%0AIiwiUHJvZHVjdCBTcG9uc29yZWQgQ29udGVudCBWaWV3ZWQiLCIxLTAtMCIs%0AWyJhbXBsaXR1ZGUiXV1d%0A',
      'X-PJAX-Container': '#pjax-container',
      'X-Requested-With': 'XMLHttpRequest',
      'Priority': 'u=3, i',
      'X-PJAX': 'true',
      'X-CSRF-Token': 'VgmLDNGYJyLLrp7uAUlaPhUZz_W4r_P1NED11JzeH4v6WEGEgAXoU2oFuZ-FMsfpK9Q2O2lvGXg37yemd3LWNg'
    }
    
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text

def scrape_reviews(company_name):
    """Scrape reviews for a company"""
    processed_reviews = []
    processed_pages = []
    failed_pages = []

    genai.configure(api_key=GOOGLE_API_KEY)

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

    for page_no in range(1, TOTAL_PAGES + 1):
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
                            "review_pros": "Example pros text",
                            "review_cons": "Example cons text",
                            "review_problems_solved": "Example problems solved",
                            "review_url": "https://www.g2.com/products/example/reviews/example-review"
                        }}

                        {get_html_for_company(company_name, page_no)}
                        """
                    ],
                }
            ]
        )
        
        response = chat_session.send_message("INSERT_INPUT_HERE")

        try:
            reviews = json.loads(response.text.replace('```json', '').replace('```',''))
            processed_reviews.extend(reviews)
            processed_pages.append(page_no)
            print(f"Page no: {page_no} done")
        except Exception as e:
            print(f"Exception {e}")
            print(f"Failed Page no: {page_no} done")
            failed_pages.append(page_no)
            continue

    return processed_reviews

@app.route('/api/scrape', methods=['POST'])
def scrape_g2_reviews():
    try:
        data = request.get_json()
        if not data or 'g2_url' not in data:
            return jsonify({'error': 'Missing G2 URL'}), 400

        g2_url = data['g2_url']
        company_name = extract_company_name(g2_url)
        
        # Scrape reviews
        reviews = scrape_reviews(company_name)
        
        # Convert to CSV
        df = pd.DataFrame(reviews)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        
        # Return CSV as string
        return jsonify({
            'success': True,
            'company': company_name,
            'csv_data': csv_buffer.getvalue(),
            'review_count': len(reviews)
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 