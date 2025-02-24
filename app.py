import requests
import csv
import io
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1eSkljelxmto_lrpUXCZzhoKByqJ-voQdKBMglS2Re30/gviz/tq?tqx=out:csv"
API_TIMEOUT = 7  # seconds

def search_google_sheet(query):
    try:
        response = requests.get(GOOGLE_SHEET_URL, timeout=5)
        response.raise_for_status()
        csv_data = io.StringIO(response.text)
        reader = csv.reader(csv_data)
        headers = [header.strip().lower() for header in next(reader, [])]
        
        keyword_idx = headers.index("keyword")
        response_idx = headers.index("response")
        
        for row in reader:
            if len(row) > max(keyword_idx, response_idx):
                if query.lower() in row[keyword_idx].lower():
                    return row[response_idx]
        return None
    except Exception as e:
        print(f"Google Sheets Error: {str(e)}")
        return None

def search_duckduckgo(query):
    try:
        response = requests.get(
            "https://api.duckduckgo.com",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=5
        )
        data = response.json()
        return data.get('AbstractText') or data.get('RelatedTopics', [{}])[0].get('Text')
    except Exception as e:
        print(f"DuckDuckGo Error: {str(e)}")
        return None

@app.route("/ask", methods=["GET"])
def handle_query():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400
    
    # Check Google Sheets first
    sheet_response = search_google_sheet(query)
    if sheet_response:
        return jsonify({
            "query": query,
            "response": sheet_response,
            "source": "Knowledge Base"
        })
    
    # Fallback to DuckDuckGo
    ddg_response = search_duckduckgo(query)
    if ddg_response:
        return jsonify({
            "query": query,
            "response": ddg_response,
            "source": "DuckDuckGo"
        })
    
    return jsonify({
        "query": query,
        "response": "I'm constantly learning! Please try another question.",
        "source": "ParadoxGPT"
    })

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
