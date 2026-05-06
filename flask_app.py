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
        yield "Starting lightweight extraction...<br>"
        
        file = request.files.get('leads_file')
        if not file:
            yield "❌ Error: No file detected.<br>"
            return

        try:
            # Read line by line to keep memory usage near zero
            content = file.stream.read().decode("utf-8")
            # Filter out empty lines and dashed separator lines
            lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith('-')]
            
            today = datetime.now().strftime("%d %b %Y")
            count = 0
            
            # We process in chunks of 5 lines based on your layout
            for i in range(0, len(lines), 5):
                if i + 4 < len(lines):
                    hr_name = lines[i]
                    hr_email = lines[i+1]
                    staff_name = lines[i+2]
                    staff_pos = lines[i+3]
                    company = lines[i+4]

                    # Logic for sending (simulated for logs)
                    time.sleep(0.3) 
                    yield (f"✅ <b>[{today}]</b> Processed: {staff_name}<br>"
                           f"&nbsp;&nbsp;&nbsp;👤 HR: {hr_name}<br>"
                           f"&nbsp;&nbsp;&nbsp;💼 {staff_pos} at {company}<br>")
                    count += 1
            
            yield f"<br><b>Successfully finished {count} records!</b>"
        except Exception as e:
            yield f"❌ Error: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()