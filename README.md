# ParadoxGPT

ParadoxGPT is a free AI chatbot that supports both **Bangla** and **English**, using **free NLP techniques** without relying on expensive third-party APIs. It can:

✅ Answer general knowledge questions using **DuckDuckGo API** & **Wikipedia API**  
✅ Read and respond from a **Google Sheet** (No Google Cloud required)  
✅ Handle **natural conversations** in Bangla & English  
✅ Be deployed for free on **Render** and shared on **GitHub**  

---

## Features

### 1️⃣ **Free NLP with Bangla & English Support**
- No paid AI models required! Uses **free NLP** to understand questions.

### 2️⃣ **DuckDuckGo & Wikipedia API for Knowledge**
- If no answer is found in Google Sheets, it searches the web for information.

### 3️⃣ **Google Sheets Integration (Without Google Cloud)**
- Reads responses from a Google Sheet **without needing a payment method**.
- Just make your sheet public and add keyword-based responses.

### 4️⃣ **Lightweight & Fast Deployment**
- Runs on **Flask** and can be deployed for free on **Render**.
- Can be easily updated via **GitHub**.

---

## How to Install & Run

### 🔹 Step 1: Clone the Repository
```bash
git clone https://github.com/your-github-username/ParadoxGPT.git
cd ParadoxGPT
```

### 🔹 Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### 🔹 Step 3: Run the Bot Locally
```bash
python app.py
```
- Open your browser and visit: `http://127.0.0.1:5000/ask?query=Bangladesh`

### 🔹 Step 4: Deploy on Render
1. Push your code to GitHub.
2. Go to [Render](https://render.com/) and create a **New Web Service**.
3. Select your **GitHub repository** and set `Start Command` as:
   ```bash
   gunicorn app:app
   ```
4. Click **Deploy** and get your live API URL!

---

## API Usage
Once deployed, use the chatbot via an API request:
```bash
https://your-render-app.com/ask?query=Your Question Here
```

Example:
```
https://your-render-app.com/ask?query=Who is the founder of Bangladesh?
```

---

## Developer Info
👤 **Developer:** Khubayb Hossain (খোবায়েব হোসেন)  
📚 **Website:** [Learn With Tonima](https://learnwithtonima.blogspot.com/)  
📞 **Contact:** +880 1753-585222  
📌 **Facebook:** [Profile Link](https://www.facebook.com/profile.php?id=100004546849052)  

### About Khubayb Hossain
Khubayb Hossain (খোবায়েব হোসেন) is a **Digital Marketer, Digital Creator, and AI Developer**. He is the creator of **ParadoxGPT** and **Learn with Tonima**, platforms focused on AI development and free education. Currently, he works as an **Officer for Data Entry, Analysis, and Presentation at Alliance Knit Composite Limited**. Previously, he was an **Assistant Officer for Data Analysis and Presentation at Scandex Textile Industries Limited**.

### Skills & Interests
- Expert in **Digital Marketing, AI Development, and Data Analysis**
- Passionate about **AI and automation**
- Marvel fan and enjoys **creating characters for comics**
- Loves **Cricket**, though he hasn’t played since 2020
- **Favorite Colors:** Blue and Black
- **Favorite Food:** His wife's cooking, especially **noodles and khichuri**

### Paranormal Experiences
Khubayb has **paranormal abilities**, which sometimes lead to **extreme anger and loss of control**. While he wants to distance himself from these experiences, he sees them as inspiration for his **comic character creations**.

### Tech & AI Work
- Currently experimenting with **Rasa on Render** and considering a **Render subscription**
- Previously attempted **Botpress**, but encountered **deployment issues**

With a strong passion for **technology, creativity, and learning**, Khubayb continues to **push boundaries in the digital space**.

---

## License
This project is open-source and free to use under the **MIT License**.
