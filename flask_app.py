import re, csv, io, smtplib, time, random
import pandas as pd
from flask import Flask, render_template, request, Response, stream_with_context
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__)

def multi_lead_parse(text):
    return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    f = request.files.get('source_file')
    if not f: return "No file uploaded", 400
    
    try:
        if f.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(f)
            raw_text = "\n".join(df.astype(str).values.flatten())
        else:
            raw_text = f.read().decode('utf-8', errors='ignore')
        
        emails = multi_lead_parse(raw_text)
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['HR_Email', 'Boss_Name', 'Staff_Name'])
        for email in emails:
            cw.writerow([email, "Manager", "Employee"])
        
        return Response(si.getvalue(), mimetype="text/csv", 
                        headers={"Content-disposition": "attachment; filename=leads.csv"})
    except Exception as e:
        return f"Scrape Error: {str(e)}", 500

@app.route('/send', methods=['POST'])
def send():
    def generate():
        f_smtp = request.files.get('smtp_file')
        f_csv = request.files.get('csv_file')
        subject_template = request.form.get('subject', 'Payroll Update')
        body_template = request.form.get('message', '')

        if not f_smtp or not f_csv:
            yield "data: Error: Missing files\n\n"
            return

        smtps = [l.decode("utf-8").strip() for l in f_smtp if ":" in l.decode("utf-8")]
        reader = list(csv.DictReader(io.StringIO(f_csv.read().decode("utf-8"))))

        yield "data: 🚀 Starting dispatch...\n\n"

        for i, row in enumerate(reader):
            user_email, app_pass = smtps[i % len(smtps)].split(':', 1)
            target = row.get('HR_Email')
            if not target: continue

            try:
                # 30 second timeout to prevent hanging
                server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
                server.starttls()
                server.login(user_email, app_pass.replace(" ", ""))
                
                sn, bn = row.get('Staff_Name', 'Staff'), row.get('Boss_Name', 'Manager')
                msg = MIMEMultipart()
                msg['From'] = formataddr((sn, user_email))
                msg['To'] = target
                msg['Subject'] = subject_template.replace("{staff_name}", sn)
                msg.attach(MIMEText(body_template.replace("{staff_name}", sn).replace("{boss_name}", bn), 'plain'))
                
                server.send_message(msg)
                server.quit()
                yield f"data: ✅ Sent to {target} via {user_email}\n\n"
                
                # Human-like delay
                time.sleep(random.randint(10, 20))
            except Exception as e:
                yield f"data: ❌ Failed {target}: {str(e)}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True)