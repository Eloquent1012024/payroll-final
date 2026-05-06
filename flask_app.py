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
        yield "🚀 Starting Final Secure Parser...<br>"
        
        file = request.files.get('leads_file')
        if not file:
            yield "❌ Error: File not received by server.<br>"
            return

        try:
            # Read the file and strip all lines of extra spaces
            raw_content = file.stream.read().decode("utf-8")
            # Only keep lines that actually have text (removes all blank lines)
            lines = [l.strip() for l in raw_content.splitlines() if l.strip()]
            
            today = datetime.now().strftime("%d %b %Y")
            count = 0
            
            # Loop through the cleaned list of lines
            for i in range(len(lines)):
                # We use the Email as the anchor point
                if "@" in lines[i]:
                    try:
                        # ANCHOR LOGIC:
                        # One line above the email is the Boss (Scoop)
                        # The lines following the email are Staff, Position, Company
                        boss_name = lines[i-1] if i > 0 else "System"
                        hr_email = lines[i]
                        staff_name = lines[i+1]
                        position = lines[i+2]
                        company = lines[i+3]

                        yield f"<b>[{today}]</b> Sending Payroll...<br>"
                        yield f"&nbsp;&nbsp;👤 Boss: {boss_name}<br>"
                        yield f"&nbsp;&nbsp;📧 From: {hr_email}<br>"
                        yield f"&nbsp;&nbsp;🎯 To: {staff_name}<br>"
                        yield f"&nbsp;&nbsp;💼 {position} at {company}<br>"
                        yield "-----------------------------------<br>"
                        
                        count += 1
                        time.sleep(0.2) # Keeps the web stream stable
                    except IndexError:
                        # Prevents crashing if the last lead is incomplete
                        continue

            if count == 0:
                yield "⚠️ No valid leads found. Check your .txt file content.<br>"
            else:
                yield f"<br>✅ <b>Completed! {count} leads extracted successfully.</b>"
                
        except Exception as e:
            yield f"❌ Error processing text: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()