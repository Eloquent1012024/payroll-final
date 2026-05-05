import re, csv, requests, io, smtplib, time, random
import pandas as pd
from flask import Flask, render_template, request, Response
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__)

# Global storage for the current session
data_store = {
    "status": "System Ready",
    "logs": [],
    "subject": "Payroll Update - {staff_name}",
    "message": "Hi {boss_name},\n\nI hope you're having a good week.\n\nI'm writing to request an update to my payroll information. Please let me know the next steps.\n\nBest,\n\n{staff_name}"
}

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # --- SECTION 1: SCRAPING ---
        if 'scrape' in request.form:
            data_store['status'] = "Scraping..."
            f = request.files.get('source_file')
            if not f or f.filename == '':
                data_store['status'] = "Error: No file selected for scraping"
                return render_template('index.html', data=data_store)

            si = io.StringIO()
            cw = csv.writer(si)
            cw.writerow(['HR_Email', 'Boss_Name', 'Staff_Name', 'Staff_Position', 'Company_Name'])
            
            try:
                if f.filename.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(f)
                    raw_text = "\n".join(df.astype(str).values.flatten())
                else:
                    raw_text = f.read().decode('utf-8', errors='ignore')
                
                found = multi_lead_parse(raw_text, cw)
                if found > 0:
                    si.seek(0)
                    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-disposition": "attachment; filename=leads.csv"})
                data_store['status'] = "No leads found in file."
            except Exception as e:
                data_store['status'] = f"Scrape Error: {str(e)}"

        # --- SECTION 2: SENDING ---
        elif 'send_emails' in request.form:
            data_store['logs'] = ["Initiating Gmail sequence..."]
            f_smtp = request.files.get('smtp_file')
            f_csv = request.files.get('csv_file')
            
            if not f_smtp or not f_csv:
                data_store['status'] = "Error: Missing SMTP or CSV file"
                return render_template('index.html', data=data_store)

            try:
                smtps = [l.decode("utf-8").strip() for l in f_smtp if ":" in l.decode("utf-8")]
                csv_content = f_csv.read().decode("utf-8")
                reader = list(csv.DictReader(io.StringIO(csv_content)))
                
                if not smtps or not reader:
                    data_store['status'] = "Error: SMTP or CSV file is empty"
                    return render_template('index.html', data=data_store)

                sent_count = 0
                for i, row in enumerate(reader):
                    user_email, app_pass = smtps[i % len(smtps)].split(':', 1)
                    target = row.get('HR_Email')
                    
                    if not target: continue

                    try:
                        # Random delay between 15-40 seconds to avoid spam flags
                        if sent_count > 0:
                            time.sleep(random.randint(15, 40)) 
                        
                        server = smtplib.SMTP("smtp.gmail.com", 587)
                        server.starttls()
                        server.login(user_email, app_pass)
                        
                        sn = row.get('Staff_Name', 'Staff')
                        bn = row.get('Boss_Name', 'Manager')
                        
                        msg = MIMEMultipart()
                        msg['From'] = formataddr((sn, user_email))
                        msg['To'] = target
                        msg['Subject'] = request.form.get('subject').replace("{staff_name}", sn)
                        
                        body = request.form.get('message').replace("{staff_name}", sn).replace("{boss_name}", bn)
                        msg.attach(MIMEText(body, 'plain'))
                        
                        server.send_message(msg)
                        server.quit()
                        
                        sent_count += 1
                        data_store['logs'].append(f"✅ Sent to: {target} (via {user_email})")
                    except Exception as e:
                        data_store['logs'].append(f"❌ Failed {target}: {str(e)}")
                
                data_store['status'] = f"Completed. Sent {sent_count} emails."
            except Exception as e:
                data_store['status'] = f"System Error: {str(e)}"

    return render_template('index.html', data=data_store)

def multi_lead_parse(text, cw):
    count = 0
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    for email in emails:
        cw.writerow([email, "Manager", "Employee", "Staff", "Company"])
        count += 1
    return count

if __name__ == "__main__":
    app.run()