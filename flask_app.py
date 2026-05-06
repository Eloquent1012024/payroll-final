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
            # Get every line that actually has text, ignoring all blank lines
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            
            today = datetime.now().strftime("%d %b %Y")
            count = 0
            
            # We search for the email address as the "Start" of a block
            for i in range(len(lines)):
                if "@" in lines[i]:
                    try:
                        # Based on Capture_6.PNG:
                        # The line BEFORE the email is the Boss (Scoop)
                        # The lines AFTER the email are Name, Position, Company
                        boss = lines[i-1] if i > 0 else "Scoop"
                        email = lines[i]
                        staff = lines[i+1]
                        pos = lines[i+2]
                        comp = lines[i+3]

                        yield f"<b>[{today}]</b> Extracting...<br>"
                        yield f"👤 Boss: {boss}<br>"
                        yield f"📧 Email: {email}<br>"
                        yield f"👤 Staff: {staff}<br>"
                        yield f"🛠️ Pos: {pos}<br>"
                        yield f"🏢 Co: {comp}<br>"
                        yield "--------------------------<br>"
                        
                        count += 1
                        time.sleep(0.2)
                    except IndexError:
                        continue

            if count == 0:
                yield "⚠️ No leads found. Check if your file matches the screenshot.<br>"
            else:
                yield f"<br><b>Done! {count} leads processed.</b>"
        except Exception as e:
            yield f"❌ Error: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()