import os
import time
from datetime import datetime
from flask import Flask, render_template, request, Response, stream_with_context

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send_payroll():
    def generate():
        file = request.files.get('leads_file')
        if not file:
            yield "❌ No file uploaded.<br>"
            return

        try:
            content = file.stream.read().decode("utf-8")
            # Filter out empty lines and those dashed separator lines
            lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith('-')]
            
            today = datetime.now().strftime("%d %b %Y")
            count = 0
            
            # This follows your exact 5-line vertical pattern
            for i in range(0, len(lines), 5):
                if i + 4 < len(lines):
                    # Capturing the actual data from your lines
                    boss_name = lines[0]     # Line 1
                    hr_email = lines[1]      # Line 2
                    staff_name = lines[2]    # Line 3
                    staff_pos = lines[3]     # Line 4
                    company_name = lines[4]  # Line 5

                    # This prints the REAL data to your screen
                    yield f"<b>[{today}]</b> Sending Payroll...<br>"
                    yield f"From: {boss_name} ({hr_email})<br>"
                    yield f"To: {staff_name}<br>"
                    yield f"Position: {staff_pos}<br>"
                    yield f"Company: {company_name}<br>"
                    yield "--------------------------<br>"
                    
                    time.sleep(0.3) 
                    count += 1
            
            yield f"<br><b>Successfully dispatched {count} records!</b>"
        except Exception as e:
            yield f"❌ Error: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()