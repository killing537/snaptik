import requests
import re
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Token yang kita temukan kita masukkan langsung (hardcode)
HARDCODED_TOKEN = "eyMTc1NjA0MjkyOA==c"

# --- Template HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eksperimen Hardcode Token</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 1rem; box-sizing: border-box; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 100%; }
        h1 { font-size: 1.5rem; color: #ffc107; }
        p.subtitle { color: #606770; margin-bottom: 1.5rem; }
        .result { margin-top: 1.5rem; }
        .result a { background-color: #198754; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; }
        .error { color: #dc3545; font-weight: bold; }
        .info { color: #0dcaf0; font-weight: bold;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Eksperimen Hardcode Token</h1>
        <p class="subtitle">Mencoba menggunakan token: {{ token_used }}</p>
        <div class="result">
            {% if download_link %}
                <p class="info">HASIL: Berhasil! Ini membuktikan token bersifat statis.</p>
                <a href="{{ download_link }}" target="_blank">Unduh Video</a>
            {% elif error %}
                <p class="error">HASIL: Gagal. {{ error }}</p>
                <p><b>Kesimpulan:</b> Ini membuktikan token bersifat dinamis (kedaluwarsa) dan harus diambil setiap kali akan digunakan.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# --- Fungsi Backend yang Hanya Menggunakan Hardcoded Token ---
def get_link_with_hardcoded_token(tiktok_url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Referer': 'https://snaptik.app/'
    }
    
    # LANGSUNG LOMPAT KE LANGKAH 2: Menggunakan token yang sudah kita simpan
    api_url = "https://snaptik.app/abc2.php"
    payload = {
        'url': tiktok_url,
        'token': HARDCODED_TOKEN, # Menggunakan token yang kita hardcode
    }
    
    print(f"Mengirim POST request ke {api_url} dengan token statis: {HARDCODED_TOKEN}")
    
    try:
        api_response = session.post(api_url, headers=headers, data=payload, timeout=20)
        api_response.raise_for_status()
        
        api_text = api_response.text
        link_search = re.search(r'href=\\"(https:\/\/snapxcdn\.com\/[^"]+)\\"', api_text)
        
        if link_search:
            download_link = link_search.group(1).replace('\\', '')
            return download_link, None
        else:
            return None, "SnapTik tidak mengembalikan link download. Kemungkinan token ditolak."

    except requests.exceptions.RequestException as e:
        return None, f"Terjadi kesalahan jaringan: {str(e)}"

# --- Routing Aplikasi Flask ---
# Cukup buka halaman utama untuk menjalankan eksperimen
@app.route('/')
def home():
    # Untuk eksperimen ini, kita gunakan URL TikTok statis agar mudah
    test_url = "https://vt.tiktok.com/ZSYgr4P2E/" 
    
    link, error = get_link_with_hardcoded_token(test_url)
    
    return render_template_string(HTML_TEMPLATE, download_link=link, error=error, token_used=HARDCODED_TOKEN)
    
