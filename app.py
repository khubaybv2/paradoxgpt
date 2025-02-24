import requests
import csv
import io
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from langdetect import detect
from sentence_transformers import SentenceTransformer
from huggingface_hub import cached_download
import numpy as np

app = Flask(__name__)
CORS(app)

# Configuration
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/gviz/tq?tqx=out:csv"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # Supports 50+ languages

# Initialize NLP model
model = SentenceTransformer(MODEL_NAME)

def load_knowledge_base():
    response = requests.get(GOOGLE_SHEET_URL)
    response.raise_for_status()
    
    knowledge = []
    reader = csv.reader(io.StringIO(response.text))
    for row in reader:
        if len(row) >= 2:
            keywords = [kw.strip() for kw in row[0].split(';')]
            response = row[1].strip()
            knowledge.append({"keywords": keywords, "response": response})
    return knowledge

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

def semantic_similarity(query, knowledge_base):
    query_embedding = model.encode(query)
    similarities = []
    
    for entry in knowledge_base:
        keyword_embeddings = model.encode(entry["keywords"])
        max_sim = np.max([np.dot(query_embedding, emb) for emb in keyword_embeddings])
        similarities.append(max_sim)
        
    return similarities

@app.route("/ask", methods=["POST"])
def handle_query():
    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    lang = detect_language(query)
    knowledge_base = load_knowledge_base()
    
    # Semantic matching
    similarities = semantic_similarity(query, knowledge_base)
    best_match_idx = np.argmax(similarities)
    
    if similarities[best_match_idx] > 0.5:  # Similarity threshold
        return jsonify({
            "response": knowledge_base[best_match_idx]["response"],
            "language": lang,
            "confidence": float(similarities[best_match_idx])
        })
    
    # Fallback to DuckDuckGo/Wikipedia (existing implementation)
    # ...

    return jsonify({
        "response": "I'm still learning. Please rephrase your question.",
        "language": lang
    })

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
