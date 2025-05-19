from flask import Flask, request, jsonify, render_template
import requests
from readability import Document
from bs4 import BeautifulSoup
import subprocess

app = Flask(__name__)

def summarize_with_llama3(text):
    prompt = (
        "Read the full content below and provide a complete summary of the entire webpage. "
        "Format the summary as clear, detailed bullet points that cover all key sections and ideas:\n\n"
        f"{text}"
    )
    result = subprocess.run(
        ['ollama', 'run', 'llama3', prompt],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    return result.stdout.strip()


@app.route('/')
def index():
    return render_template('index.html')  # Serve the index.html page

@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL missing'}), 400

    try:
        response = requests.get(url)
        doc = Document(response.text)
        html = doc.summary()
        soup = BeautifulSoup(html, 'html.parser')
        main_text = soup.get_text()

        summary = summarize_with_llama3(main_text[:3000])  # Truncate to prevent long input issues
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
