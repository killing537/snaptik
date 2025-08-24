import requests
import re
from flask import Flask, render_template_string

app = Flask(__name__)

# --- Template HTML untuk Menampilkan Hasil Eksperimen ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eksperimen Scraping Token</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; padding: 2rem; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }
        h1 { color: #0d6efd; }
        h2 { border-bottom: 2px solid #eee; padding-bottom: 0.5rem; margin-top: 2rem; }
        code { background-color: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; display: block; }
        .success { color: #198754; font-weight: bold; }
        .failure { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hasil Eksperimen: Scraping Token dari SnapTik</h1>
        
        <h2>Hasil Pencarian Token:</h2>
        {% if token %}
            <p class="success">Token ditemukan!</p>
            <code>{{ token }}</code>
        {% else %}
            <p class="failure">Token TIDAK ditemukan di dalam HTML awal.</p>
            <p>Ini membuktikan bahwa token dibuat oleh JavaScript setelah halaman dimuat, sehingga tidak terlihat oleh library 'requests'.</p>
        {% endif %}

        <h2>HTML Mentah yang Diterima (Potongan):</h2>
        <code>{{ raw_html }}</code>
    </div>
</body>
</html>
"""

def scrape_initial_token():
    """
    Fungsi ini mengambil halaman utama SnapTik dan mencoba mengekstrak token.
    """
    url = "https://snaptik.app/ID2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    
    try:
        print("Mencoba mengambil HTML dari SnapTik...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
        print("HTML berhasil diambil.")

        print("Mencari token di dalam HTML...")
        # Pola regex untuk mencari: <input name="token" value="NILAI_TOKEN">
        search = re.search(r'<input name="token" value="([^"]+)">', html_content)
        
        if search and search.group(1):
            # Jika ditemukan dan nilainya tidak kosong
            token = search.group(1)
            print(f"Token ditemukan: {token}")
            return token, html_content
        else:
            # Jika tidak ditemukan atau nilainya kosong
            print("Token tidak ditemukan atau value-nya kosong.")
            return None, html_content

    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil halaman: {e}")
        return None, f"Error saat request: {str(e)}"

# --- Routing Aplikasi Flask ---
@app.route('/')
def home():
    token, raw_html = scrape_initial_token()
    # Kita potong HTML mentah agar tidak terlalu panjang saat ditampilkan
    raw_html_snippet = (raw_html[:30000] + '...') if raw_html else "Tidak ada HTML yang diterima."
    
    # Menampilkan hasil di halaman web
    return render_template_string(HTML_TEMPLATE, token=token, raw_html=raw_html_snippet)

