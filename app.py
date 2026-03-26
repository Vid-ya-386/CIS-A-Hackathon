from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import hashlib

app = Flask(__name__)

def get_clean_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)

        # handle bad responses
        if response.status_code != 200:
            return "ERROR"

        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text()
        return " ".join(text.split())

    except Exception:
        return "ERROR"

def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    if request.method == "POST":
        url = request.form.get("url")

        if not url.startswith("http"):
            url = "https://" + url

        old = get_clean_text(url)
        new = get_clean_text(url)

        if old == "ERROR" or new == "ERROR":
            result = "⚠️ Could not fetch website (blocked or invalid URL)"
        elif get_hash(old) == get_hash(new):
            result = "✅ No change detected"
        else:
            result = "⚠️ Website changed!"

    return render_template_string("""
        <h2>Website Change Detector</h2>
        <form method="post">
            <input type="text" name="url" placeholder="Enter URL" required>
            <button type="submit">Check</button>
        </form>
        <p>{{result}}</p>
    """, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)