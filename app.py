from flask import Flask, request, render_template_string
from markupsafe import escape
import requests
import re

app = Flask(__name__)

# --- Template HTML disatukan di sini agar mudah ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python TikTok Downloader - Debug Mode</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 90%; width: 800px; margin: 2rem auto; }
        h1 { font-size: 1.5rem; color: #1877f2; }
        input[type="text"] { width: 100%; padding: 12px; margin: 1rem 0; border: 1px solid #dddfe2; border-radius: 6px; box-sizing: border-box; }
        button { background-color: #1877f2; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: bold; width: 100%; }
        button:hover { background-color: #166fe5; }
        .result { margin-top: 1.5rem; text-align: left; }
        .error { color: #f02849; font-weight: bold; background-color: #fff0f0; border: 1px solid #f02849; padding: 1rem; border-radius: 6px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <h1>TikTok Downloader (Debug Mode)</h1>
        <form method="post">
            <input type="text" name="tiktok_url" placeholder="Tempel URL TikTok di sini..." required>
            <button type="submit">Download</button>
        </form>
        <div class="result">
            {% if error %}
                <h3>HTML Response from Server:</h3>
                <pre class="error"><code>{{ error }}</code></pre>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# --- Fungsi Backend yang Diperbarui untuk DEBUGGING ---
def get_download_link(tiktok_url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        res = session.head(tiktok_url, headers=headers, allow_redirects=True, timeout=10)
        full_url = res.url
        
        session.get('https://ssstik.io/', headers=headers, timeout=15)
        
        api_url = "https://ssstik.io/abc?url=dl"
        payload = {'id': full_url, 'locale': 'en'}
        
        api_response = session.post(api_url, data=payload, headers=headers, timeout=15)
        api_response.raise_for_status()

        download_search = re.search(r'href="([^"]+)" class="pure-button pure-button-primary is-center u-bl dl-button download_link without_watermark"', api_response.text)
        
        if download_search:
            return "BERHASIL MENEMUKAN LINK! (Tidak perlu debug)", None
        else:
            return None, api_response.text

    except requests.exceptions.RequestException as e:
        return None, f"Terjadi error pada level request: {str(e)}"

# --- Routing Aplikasi Flask ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_input = request.form.get('tiktok_url')
        link, error_message = get_download_link(url_input)
        
        return render_template_string(HTML_TEMPLATE, error=escape(error_message or "Tidak ada error, namun link juga tidak ditemukan."))
    
    return render_template_string(HTML_TEMPLATE)
    
