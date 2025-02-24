import requests
import csv
import io
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1eSkljelxmto_lrpUXCZzhoKByqJ-voQdKBMglS2Re30/gviz/tq?tqx=out:csv"
HEADER_MAPPING = {
    "keyword": ["keyword", "keywords", "key word"],
    "response": ["response", "answer", "reply"]
}

def find_column_index(headers, possible_names):
    for idx, header in enumerate(headers):
        cleaned_header = header.strip().lower()
        if cleaned_header in possible_names:
            return idx
    return None

def search_google_sheet(query):
    try:
        response = requests.get(GOOGLE_SHEET_URL, timeout=10)
        response.raise_for_status()
        
        # Parse CSV with error handling
        csv_data = io.StringIO(response.text)
        reader = csv.reader(csv_data)
        
        # Read headers with fallback
        try:
            raw_headers = next(reader)
        except StopIteration:
            app.logger.error("Empty Google Sheet response")
            return None

        # Clean and normalize headers
        headers = [header.strip().lower() for header in raw_headers]
        
        # Find columns using flexible matching
        keyword_idx = find_column_index(headers, HEADER_MAPPING["keyword"])
        response_idx = find_column_index(headers, HEADER_MAPPING["response"])

        if None in [keyword_idx, response_idx]:
            missing = []
            if keyword_idx is None: missing.append("keyword")
            if response_idx is None: missing.append("response")
            app.logger.error(f"Missing columns in sheet: {', '.join(missing)}")
            return None

        # Search through rows
        for row in reader:
            try:
                if len(row) > max(keyword_idx, response_idx):
                    keywords = [kw.strip().lower() for kw in row[keyword_idx].split(";")]
                    if query.lower().strip() in keywords:
                        return row[response_idx].strip()
            except IndexError:
                continue

        return None

    except Exception as e:
        app.logger.error(f"Google Sheets Error: {str(e)}")
        return None

def search_duckduckgo(query):
    try:
        response = requests.get(
            "https://api.duckduckgo.com",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "no_redirect": 1,
                "skip_disambig": 1
            },
            timeout=10
        )
        data = response.json()
        
        # Improved response extraction
        return (
            data.get("AbstractText") 
            or (data.get("RelatedTopics")[0]["Text"] if data.get("RelatedTopics") else None)
            or data.get("Definition")
            or data.get("Answer")
        )
    except Exception as e:
        app.logger.error(f"DuckDuckGo Error: {str(e)}")
        return None

@app.route("/ask", methods=["GET"])
def handle_query():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400
    
    # Try Google Sheets with improved error handling
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
