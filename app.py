import requests
import re
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- Template HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader (SnapTik Final)</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 1rem; box-sizing: border-box; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 100%; }
        h1 { font-size: 1.5rem; color: #0d6efd; }
        p.subtitle { color: #606770; margin-bottom: 1.5rem; }
        input[type="text"] { width: 100%; padding: 12px; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; box-sizing: border-box; }
        button { background-color: #0d6efd; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: bold; width: 100%; transition: background-color 0.2s; }
        button:hover { background-color: #0b5ed7; }
        .result { margin-top: 1.5rem; }
        .result a { background-color: #198754; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; }
        .result a:hover { background-color: #157347; }
        .error { color: #dc3545; font-weight: bold; }
        .loader { display: none; margin: 1rem auto; border: 4px solid #f3f3f3; border-radius: 50%; border-top: 4px solid #0d6efd; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>TikTok Downloader</h1>
        <p class="subtitle">Ditenagai oleh SnapTik (Versi Final)</p>
        <form method="post" onsubmit="document.getElementById('loader').style.display='block'">
            <input type="text" name="tiktok_url" placeholder="Tempel URL TikTok di sini..." required>
            <button type="submit">Download</button>
        </form>
        <div class="loader" id="loader"></div>
        <div class="result">
            {% if download_link %}
                <p>Video berhasil diproses!</p>
                <a href="{{ download_link }}" target="_blank">Unduh Video Tanpa Watermark</a>
            {% endif %}
            {% if error %}
                <p class="error">Error: {{ error }}</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# --- Fungsi Backend Final untuk SnapTik ---
def get_final_snaptik_link(tiktok_url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    
    try:
        # --- LANGKAH 1: Mengambil halaman utama untuk mendapatkan token ---
        home_url = "https://snaptik.app/ID2"
        print(f"Mengambil halaman utama dari {home_url}...")
        home_response = session.get(home_url, headers=headers, timeout=15)
        home_response.raise_for_status()
        html_content = home_response.text
        print("Halaman utama berhasil diambil.")

        search = re.search(r'<input name="token" value="([^"]+)">', html_content)
        if not search or not search.group(1):
            return None, "Gagal menemukan token di halaman utama SnapTik."
        
        token = search.group(1)
        print(f"Token ditemukan: {token}")

        # --- LANGKAH 2: Menggunakan token untuk mengirim request POST ke API ---
        api_url = "https://snaptik.app/abc2.php"
        payload = {
            'url': tiktok_url,
            'token': eyMTc1NjA0MjkyOA==c,
        }
        headers['Referer'] = 'https://snaptik.app/ID2' # Tambahkan referer
        print(f"Mengirim request POST ke {api_url}...")
        
        api_response = session.post(api_url, headers=headers, data=payload, timeout=20)
        api_response.raise_for_status()
        print("Request POST berhasil.")

        # --- LANGKAH 3: Mengekstrak link download dari respons ---
        api_text = api_response.text
        link_search = re.search(r'href=\\"(https:\/\/snapxcdn\.com\/[^"]+)\\"', api_text)
        
        if link_search:
            download_link = link_search.group(1).replace('\\', '')
            print(f"Link download ditemukan: {download_link}")
            return download_link, None
        else:
            print("Link download tidak ditemukan di dalam respons API.")
            return None, "SnapTik tidak mengembalikan link download. Video mungkin tidak valid atau sistem telah berubah."

    except requests.exceptions.RequestException as e:
        print(f"Terjadi error: {e}")
        return None, f"Terjadi kesalahan jaringan: {str(e)}"

# --- Routing Aplikasi Flask ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_input = request.form.get('tiktok_url')
        if not url_input:
            return render_template_string(HTML_TEMPLATE, error="URL tidak boleh kosong.")
        
        link, error = get_final_snaptik_link(url_input)
        
        if link:
            return render_template_string(HTML_TEMPLATE, download_link=link)
        else:
            return render_template_string(HTML_TEMPLATE, error=error)
    
    return render_template_string(HTML_TEMPLATE)
            
