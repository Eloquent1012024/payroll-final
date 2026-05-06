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
        yield "Reading leads separated by dashed lines...<br>"
        
        leads_file = request.files.get('leads_file')
        if not leads_file:
            yield "❌ Error: No leads file uploaded.<br>"
            return

        try:
            # Read the file
            content = leads_file.stream.read().decode("utf-8")
            
            # Split the text into "blocks" using the dashed lines
            # This handles lines like ----------- or -----------------------
            blocks = [b.strip() for b in content.split('-') if b.strip() and len(b.strip()) > 20]
            
            today_date = datetime.now().strftime("%d %b %Y") # e.g., 06 May 2026
            count = 0

            for block in blocks:
                # Split each block into individual lines and remove empty ones
                lines = [line.strip() for line in block.splitlines() if line.strip()]
                
                # We expect at least 5 pieces of info per block
                if len(lines) >= 5:
                    hr_name = lines[0]
                    hr_email = lines[1]
                    staff_name = lines[2]
                    position = lines[3]
                    company = lines[4]

                    # SIMULATED SENDING LOGIC
                    time.sleep(0.4) 
                    yield (f"✅ <b>[{today_date}]</b> Sent to: {staff_name}<br>"
                           f"&nbsp;&nbsp;&nbsp;📍 {position} at {company}<br>")
                    count += 1
            
            yield f"<br><b>Successfully dispatched {count} payroll records!</b>"
            
        except Exception as e:
            yield f"❌ Error parsing dashed blocks: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()