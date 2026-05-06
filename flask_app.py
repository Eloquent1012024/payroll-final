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
        yield "🚀 Initializing Final Parser...<br>"
        
        file = request.files.get('leads_file')
        if not file:
            yield "❌ Error: File not received.<br>"
            return

        try:
            # Read and filter out empty lines immediately to keep it lightweight
            content = file.stream.read().decode("utf-8")
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            
            today = datetime.now().strftime("%d %b %Y")
            count = 0
            
            for i in range(len(lines)):
                # We use the email address as the 'Anchor'
                if "@" in lines[i]:
                    try:
                        # Based on your Notepad screenshot:
                        # The line BEFORE the email is the Boss (e.g., Scoop)
                        boss_name = lines[i-1] if i > 0 else "Unknown Boss"
                        hr_email = lines[i]
                        
                        # The 3 lines AFTER the email are Staff, Position, Company
                        staff_name = lines[i+1]
                        position = lines[i+2]
                        company = lines[i+3]

                        yield f"<b>[{today}]</b> Dispatched to: {staff_name}<br>"
                        yield f"&nbsp;&nbsp;👤 Boss: {boss_name}<br>"
                        yield f"&nbsp;&nbsp;💼 {position} @ {company}<br>"
                        yield "-----------------------------------<br>"
                        
                        count += 1
                        time.sleep(0.2) # Small delay to ensure the stream displays nicely
                    except IndexError:
                        # This prevents a crash if a lead is missing a line at the end
                        continue

            if count == 0:
                yield "⚠️ No leads found. Please check your .txt format.<br>"
            else:
                yield f"<br>✅ <b>Success! {count} records processed.</b>"
                
        except Exception as e:
            yield f"❌ System Error: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()