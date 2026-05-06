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
            # We read the raw lines, including the blank ones
            content = file.stream.read().decode("utf-8")
            all_lines = content.splitlines()
            
            # Remove trailing whitespace but keep the empty lines
            lines = [l.strip() for l in all_lines]
            
            today = datetime.now().strftime("%d %b %Y")
            count = 0
            
            # We look for 'Scoop' to start a new block
            for i in range(len(lines)):
                if "Scoop" in lines[i]:
                    try:
                        # Follows your Notepad screenshot layout:
                        # Scoop (i)
                        # Email (i+1)
                        # [Blank Line] (i+2)
                        # Name (i+3)
                        # Position (i+4)
                        # Company (i+5)
                        
                        boss = lines[i]
                        email = lines[i+1]
                        staff = lines[i+3]
                        pos = lines[i+4]
                        comp = lines[i+5]

                        yield f"<b>[{today}]</b> Processing...<br>"
                        yield f"👤 Boss: {boss}<br>"
                        yield f"📧 HR: {email}<br>"
                        yield f"👤 Staff: {staff}<br>"
                        yield f"🛠️ Pos: {pos}<br>"
                        yield f"🏢 Co: {comp}<br>"
                        yield "--------------------------<br>"
                        
                        count += 1
                        time.sleep(0.3)
                    except IndexError:
                        continue

            yield f"<br><b>Finished! {count} leads captured.</b>"
        except Exception as e:
            yield f"❌ Error: {str(e)}<br>"

    return Response(stream_with_context(generate()))

if __name__ == "__main__":
    app.run()