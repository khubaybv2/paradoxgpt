import requests
import gspread
from flask import Flask, request, jsonify

app = Flask(__name__)

# Google Sheets Public URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1eSkljelxmto_lrpUXCZzhoKByqJ-voQdKBMglS2Re30/gviz/tq?tqx=out:csv"

def search_google_sheet(query):
    response = requests.get(GOOGLE_SHEET_URL)
    if response.status_code != 200:
        return "Error fetching Google Sheets data."
    
    data = response.text.split("\n")  # Split CSV data into rows
    headers = data[0].split(",")  # Get column names
    rows = [row.split(",") for row in data[1:] if row]  # Extract rows

    keyword_col = headers.index("Keyword")  # Find Keyword column
    response_col = headers.index("Response")  # Find Response column

    for row in rows:
        if query.lower() in row[keyword_col].lower():
            return row[response_col]  # Return matched response

    return "No data found in Google Sheets."

@app.route("/ask", methods=["GET"])
def ask_paradoxgpt():
    query = request.args.get("query")
    if not query:
        return jsonify({"response": "Please provide a query."})

    response = search_google_sheet(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
