import os
from flask import Flask, request, render_template_string
import requests
from urllib.parse import unquote

app = Flask(__name__)

# --- Template HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader (SnapTik)</title>
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
        <p class="subtitle">Ditenagai oleh SnapTik</p>
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

# --- Fungsi Backend Baru Menggunakan SnapTik ---
def get_download_link_from_snaptik(tiktok_url):
    """
    Mencoba mendapatkan link download dengan meniru request browser ke SnapTik.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Origin': 'https://snaptik.app',
        'Referer': 'https://snaptik.app/',
    }
    
    try:
        # Kunjungan awal untuk mendapatkan cookie sesi
        session = requests.Session()
        session.get("https://snaptik.app", headers=headers, timeout=15)
        
        # Request utama untuk mendapatkan link
        api_url = "https://snaptik.app/abc2.php"
        params = {'url': tiktok_url}
        
        response = session.get(api_url, params=params, headers=headers, timeout=20)
        response.raise_for_status()
        
        # Respons dari SnapTik agak rumit, kita perlu mengekstrak link dari skrip javascript
        # Mencari token download yang di-decode
        # Contoh: "decoding_fun(..." -> kita cari isinya
        raw_text = response.text
        
        # Pola untuk menemukan link download di dalam fungsi javascript
        import re
        search = re.search(r'href=\\"(https:\/\/snapxcdn\.com\/[^"]+)\\"', raw_text)

        if search:
            download_link = search.group(1).replace('\\', '')
            return download_link, None
        else:
            return None, "Tidak bisa menemukan link download di respons SnapTik. Mungkin video tidak valid atau SnapTik mengubah sistemnya."

    except requests.exceptions.Timeout:
        return None, "Koneksi ke server SnapTik habis waktu (timeout)."
    except requests.exceptions.RequestException as e:
        print(f"SnapTik Request Error: {e}")
        return None, "Terjadi kesalahan saat menghubungi server SnapTik."

# --- Routing Aplikasi Flask ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_input = request.form.get('tiktok_url')
        if not url_input:
            return render_template_string(HTML_TEMPLATE, error="URL tidak boleh kosong.")
        
        link, error = get_download_link_from_snaptik(url_input)
        
        if link:
            return render_template_string(HTML_TEMPLATE, download_link=link)
        else:
            return render_template_string(HTML_TEMPLATE, error=error)
    
    return render_template_string(HTML_TEMPLATE)
        
