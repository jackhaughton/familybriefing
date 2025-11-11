from datetime import datetime, time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="static")

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'barrowcrofts-c291853a7c29.json'

# Google Calendar API scope for read-only access
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Create credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the calendar service
service = build('calendar', 'v3', credentials=credentials)

# The calendar ID (use 'primary' for the main one, or a specific ID)
calendar_id = '476736e096908cbcd1848c143f7194abd53a5e19c008a23040809f5d4dc11765@group.calendar.google.com'

# Fetch today's events
def get_todays_items():
    tz = pytz.timezone("Europe/London")
    now = datetime.now(tz)
    start_of_day = tz.localize(datetime.combine(now.date(), time.min))
    end_of_day = tz.localize(datetime.combine(now.date(), time.max))
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return []
    else:
        return [e['summary'] for e in events]

@app.route("/today", methods=["GET"])
def get_items():
    return jsonify(get_todays_items())

# Serve the root index.html from the static directory
@app.route("/", methods=["GET"])
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Optional: serve all other static files manually if needed
@app.route("/static/<path:path>", methods=["GET"])
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
