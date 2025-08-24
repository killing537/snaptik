from flask import Flask, request, render_template_string
import requests
import re

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# --- Template HTML disatukan di sini agar mudah ---
# Ini adalah tampilan antarmuka web untuk aplikasi kita
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python TikTok Downloader</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 90%; }
        h1 { font-size: 1.5rem; color: #1877f2; }
        input[type="text"] { width: 100%; padding: 12px; margin: 1rem 0; border: 1px solid #dddfe2; border-radius: 6px; box-sizing: border-box; }
        button { background-color: #1877f2; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: bold; width: 100%; }
        button:hover { background-color: #166fe5; }
        .result { margin-top: 1.5rem; }
        .result a { background-color: #42b72a; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; }
        .result a:hover { background-color: #36a420; }
        .error { color: #f02849; font-weight: bold; }
        .loader { display: none; margin: 1rem auto; border: 4px solid #f3f3f3; border-radius: 50%; border-top: 4px solid #1877f2; width: 40px; height: 40px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>TikTok Video Downloader</h1>
        <form method="post" onsubmit="showLoader()">
            <input type="text" name="tiktok_url" placeholder="Tempel URL TikTok di sini..." required>
            <button type="submit">Download</button>
        </form>
        <div class="loader" id="loader"></div>
        <div class="result">
            {% if download_link %}
                <p>Video berhasil diproses!</p>
                <a href="{{ download_link }}" target="_blank">Klik di sini untuk Mengunduh Video</a>
            {% endif %}
            {% if error %}
                <p class="error">{{ error }}</p>
            {% endif %}
        </div>
    </div>
    <script>
        function showLoader() {
            document.getElementById('loader').style.display = 'block';
        }
    </script>
</body>
</html>
"""

# --- Fungsi Backend untuk Mengambil Link Download ---
def get_download_link(tiktok_url):
    """
    Fungsi ini berkomunikasi dengan API ssstik.io untuk mendapatkan link download.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    api_url = "https://ssstik.io/abc?url=dl"
    payload = {'id': tiktok_url, 'locale': 'en'}

    try:
        # Menggunakan session untuk menangani cookies
        session = requests.Session()
        session.get('https://ssstik.io/', headers=headers, timeout=15) # Kunjungan awal untuk sesi
        
        response = session.post(api_url, data=payload, headers=headers, timeout=15)
        response.raise_for_status() # Cek jika ada error HTTP

        # Mencari link download video tanpa watermark di dalam respons HTML
        download_search = re.search(r'href="([^"]+)" class="pure-button pure-button-primary is-center u-bl dl-button download_link without_watermark"', response.text)
        
        if download_search:
            return download_search.group(1) # Mengembalikan link jika ditemukan
        else:
            return None # Mengembalikan None jika tidak ditemukan
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

# --- Routing Aplikasi Flask ---
# Ini mengatur bagaimana aplikasi merespons permintaan dari browser
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Jika pengguna mengirimkan form (metode POST)
        url_input = request.form.get('tiktok_url')
        if not url_input:
            return render_template_string(HTML_TEMPLATE, error="URL tidak boleh kosong.")
        
        # Panggil fungsi backend untuk mendapatkan link
        link = get_download_link(url_input)
        
        if link:
            # Jika link ditemukan, tampilkan halaman dengan link download
            return render_template_string(HTML_TEMPLATE, download_link=link)
        else:
            # Jika link tidak ditemukan, tampilkan pesan error
            return render_template_string(HTML_TEMPLATE, error="Gagal mendapatkan link download. Pastikan URL valid dan coba lagi.")
    
    # Jika pengguna baru membuka halaman (metode GET)
    return render_template_string(HTML_TEMPLATE)

# Bagian ini tidak wajib untuk Vercel, tapi berguna untuk tes lokal
if __name__ == '__main__':
    app.run(debug=True)
    
