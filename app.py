import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Google Sheets Public URL (CSV export link)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1eSkljelxmto_lrpUXCZzhoKByqJ-voQdKBMglS2Re30/gviz/tq?tqx=out:csv"

def fetch_google_sheet_data():
    """Fetch data from the Google Sheets public CSV link."""
    try:
        response = requests.get(GOOGLE_SHEET_URL)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        data = response.text.split("\n")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google Sheets data: {e}")
        return None

def search_google_sheet(query):
    """Search for the query in the Google Sheets and return a response."""
    data = fetch_google_sheet_data()

    if not data:
        return "Sorry, there was an error retrieving data. Please try again later."

    headers = data[0].split(",")  # The first row contains headers
    rows = [row.split(",") for row in data[1:] if row]  # Rest are the data rows

    # Ensure the expected columns exist
    if "Keyword" not in headers or "Response" not in headers:
        return "Error: Missing 'Keyword' or 'Response' column in the sheet."

    keyword_col = headers.index("Keyword")
    response_col = headers.index("Response")

    # Search for the query in the Keyword column
    for row in rows:
        if query.lower() in row[keyword_col].lower():  # Case insensitive search
            return row[response_col]  # Return matched response

    return "Sorry, I couldn't find an answer to your question. Please try again with a different query."

@app.route("/ask", methods=["GET"])
def ask_paradoxgpt():
    """Handle the incoming GET request for the chatbot."""
    query = request.args.get("query")
    
    # Validate if query parameter is provided
    if not query:
        return jsonify({"response": "Please provide a query."})

    response = search_google_sheet(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
