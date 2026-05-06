import os
import pandas as pd
from flask import Flask, render_template, request, Response, stream_with_context
import time

app = Flask(__name__)

# Mock function for scraping - Update this with your specific scraping logic
def scrape_leads(target_url):
    # This is a template; replace with your actual BeautifulSoup/Selenium logic
    # Ensure it returns a list of dictionaries with 'Company' and 'Position'
    return [
        {"Name": "John Doe", "Email": "john@example.com", "Company": "Tech Corp", "Position": "Manager"},
        {"Name": "Jane Smith", "Email": "jane@example.com", "Company": "Design Hub", "Position": "Director"}
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_payroll():
    def generate():
        yield "Starting process...<br>"
        
        # 1. Get the files
        smtp_file = request.files.get('smtp_file')
        leads_file = request.files.get('leads_file')

        if not smtp_file or not leads_file:
            yield "❌ Error: Missing files.<br>"
            return

        # 2. Process Leads (Capturing Company & Position)
        try:
            df = pd.read_csv(leads_file)
            # Ensure columns exist even if empty
            for col in ['Company', 'Position']:
                if col not in df.columns:
                    df[col] = "N/A"
            
            yield f"Found {len(df)} leads. Starting dispatch...<br>"
            
            for index, row in df.iterrows():
                name = row.get('Name', 'Valued Staff')
                email = row.get('Email')
                company = row.get('Company', 'the company')
                pos = row.get('Position', 'Staff')

                if email:
                    # SIMULATED SENDING LOGIC
                    time.sleep(1) 
                    yield f"✅ Sent to {name} ({pos}) at {company} - {email}<br>"
                else:
                    yield f"⚠️ Skipped row {index+1}: No email found.<br>"

            yield "<br><b>All tasks completed successfully!</b>"
        except Exception as e:
            yield f"❌ Critical Error: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)