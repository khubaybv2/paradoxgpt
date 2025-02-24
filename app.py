import requests
import gspread
import csv
import io
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1eSkljelxmto_lrpUXCZzhoKByqJ-voQdKBMglS2Re30/gviz/tq?tqx=out:csv"
MAX_WIKI_RESULTS = 3  # Number of Wikipedia results to return

def search_google_sheet(query):
    try:
        response = requests.get(GOOGLE_SHEET_URL, timeout=5)
        response.raise_for_status()
    except (requests.RequestException, requests.Timeout):
        return None

    try:
        # Use CSV module for proper parsing
        csv_data = io.StringIO(response.text)
        reader = csv.reader(csv_data)
        headers = [header.strip().lower() for header in next(reader, [])]
        
        if not headers:
            return None

        # Find column indices safely
        try:
            keyword_idx = headers.index("keyword")
            response_idx = headers.index("response")
        except ValueError:
            return None

        # Search rows
        for row in reader:
            if len(row) > max(keyword_idx, response_idx):
                keywords = [kw.strip().lower() for kw in row[keyword_idx].split(';')]
                if query.lower().strip() in keywords:
                    return row[response_idx].strip()
        
        return None

    except (csv.Error, IndexError):
        return None

def search_duckduckgo(query):
    try:
        response = requests.get(
            "https://api.duckduckgo.com",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "no_redirect": 1
            },
            timeout=5
        )
        data = response.json()
        
        # Prioritize different response sections
        if data.get("AbstractText"):
            return data["AbstractText"]
        if data.get("RelatedTopics"):
            return data["RelatedTopics"][0]["Text"]
        if data.get("Definition"):
            return data["Definition"]
        
        return None
    except (requests.RequestException, KeyError, IndexError):
        return None

def search_wikipedia(query):
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": MAX_WIKI_RESULTS
            },
            timeout=5
        )
        data = response.json()
        results = data.get("query", {}).get("search", [])
        
        if not results:
            return None

        # Return first 3 results as bullet points
        return "\n".join([
            f"• {result['title']}: {result['snippet']}"
            for result in results[:MAX_WIKI_RESULTS]
        ])
    except (requests.RequestException, KeyError):
        return None

@app.route("/ask", methods=["GET"])
def handle_query():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({
            "error": "Please provide a query parameter",
            "example": "/ask?query=your+question"
        }), 400

    # Search sources in priority order
    sources = [
        ("Google Sheets", search_google_sheet),
        ("DuckDuckGo", search_duckduckgo),
        ("Wikipedia", search_wikipedia)
    ]

    for source_name, search_func in sources:
        result = search_func(query)
        if result:
            return jsonify({
                "query": query,
                "response": result,
                "source": source_name
            })

    return jsonify({
        "query": query,
        "response": "Sorry, I couldn't find information on that topic.",
        "source": "No sources available"
    }), 404

@app.route("/")
def home():
    return jsonify({
        "status": "running",
        "endpoints": {
            "/ask": "GET parameter ?query=your+question"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
