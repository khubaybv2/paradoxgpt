import requests
import csv
import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from difflib import SequenceMatcher

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins for testing

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1eSkljelxmto_lrpUXCZzhoKByqJ-voQdKBMglS2Re30/gviz/tq?tqx=out:csv"
HEADER_MAPPING = {
    "keyword": ["keyword", "keywords", "key word"],
    "response": ["response", "answer", "reply"]
}
SIMILARITY_THRESHOLD = 0.8  # 80% match required

def find_column_index(headers, possible_names):
    for idx, header in enumerate(headers):
        if header.strip().lower() in possible_names:
            return idx
    return None

def get_best_match(query, candidates):
    best_ratio = 0
    best_match = None
    for candidate in candidates:
        ratio = SequenceMatcher(None, query, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate
    return best_match if best_ratio >= SIMILARITY_THRESHOLD else None

def search_google_sheet(query):
    try:
        response = requests.get(GOOGLE_SHEET_URL, timeout=10)
        response.raise_for_status()
        
        csv_data = io.StringIO(response.text)
        reader = csv.reader(csv_data)
        raw_headers = next(reader, [])
        
        headers = [header.strip().lower() for header in raw_headers]
        keyword_idx = find_column_index(headers, HEADER_MAPPING["keyword"])
        response_idx = find_column_index(headers, HEADER_MAPPING["response"])

        if None in [keyword_idx, response_idx]:
            return None

        candidates = {}
        for row in reader:
            if len(row) > max(keyword_idx, response_idx):
                keywords = [kw.strip().lower() for kw in row[keyword_idx].split(";")]
                for kw in keywords:
                    candidates[kw] = row[response_idx].strip()

        best_match = get_best_match(query.lower(), candidates.keys())
        return candidates.get(best_match)

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
        return data.get("AbstractText") or \
               (data.get("RelatedTopics")[0]["Text"] if data.get("RelatedTopics") else None)
    except Exception as e:
        app.logger.error(f"DuckDuckGo Error: {str(e)}")
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
                "srlimit": 1
            },
            timeout=10
        )
        data = response.json()
        if data["query"]["search"]:
            page_id = data["query"]["search"][0]["pageid"]
            extract = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "pageids": page_id,
                    "format": "json",
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True
                }
            ).json()
            return extract["query"]["pages"][str(page_id)]["extract"]
        return None
    except Exception as e:
        app.logger.error(f"Wikipedia Error: {str(e)}")
        return None

@app.route("/ask", methods=["POST"])
def handle_query():
    query = request.json.get("query", "").strip().lower()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    response = None
    source = "ParadoxGPT"
    
    # Search hierarchy
    sheet_response = search_google_sheet(query)
    if sheet_response:
        response = sheet_response
        source = "Knowledge Base"
    else:
        ddg_response = search_duckduckgo(query)
        if ddg_response:
            response = ddg_response
            source = "DuckDuckGo"
        else:
            wiki_response = search_wikipedia(query)
            if wiki_response:
                response = wiki_response
                source = "Wikipedia"

    return jsonify({
        "query": query,
        "response": response or "I'm still learning. Please ask me something else!",
        "source": source
    })

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
