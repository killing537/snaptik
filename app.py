from flask import Flask, request, render_template_string
import requests
import re

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# --- Template HTML disatukan di sini agar mudah ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
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
        .result a { background-color: #42b72a; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; }
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

# --- Fungsi Backend yang Diperbarui ---
def get_download_link(tiktok_url):
    """
    Fungsi ini berkomunikasi dengan API ssstik.io untuk mendapatkan link download.
    Sekarang sudah bisa menangani URL singkat (vt.tiktok.com).
    """
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        # Langkah 1: Ubah URL singkat menjadi URL panjang.
        # Kita gunakan HEAD request agar efisien, karena hanya butuh header-nya.
        res = session.head(tiktok_url, headers=headers, allow_redirects=True, timeout=10)
        full_url = res.url # Ini akan berisi URL final setelah semua pengalihan

        if "tiktok.com" not in full_url:
             return None, "URL yang Anda masukkan sepertinya bukan dari TikTok."

        # Langkah 2: Gunakan URL panjang untuk berinteraksi dengan ssstik.io
        session.get('https://ssstik.io/', headers=headers, timeout=15)
        
        # Langkah 3: Siapkan data untuk dikirim ke API ssstik.io
        api_url = "https://ssstik.io/abc?url=dl"
        payload = {'id': full_url, 'locale': 'en'} # Gunakan full_url di sini!
        
        api_response = session.post(api_url, data=payload, headers=headers, timeout=15)
        api_response.raise_for_status()

        # Langkah 4: Cari link download di dalam respons HTML
        download_search = re.search(r'href="([^"]+)" class="pure-button pure-button-primary is-center u-bl dl-button download_link without_watermark"', api_response.text)
        
        if download_search:
            return download_search.group(1), None # Mengembalikan (link, None) jika berhasil
        else:
            return None, "Tidak dapat menemukan link download. Video mungkin bersifat privat atau situs downloader sedang diperbarui."

    except requests.exceptions.Timeout:
        return None, "Koneksi ke server downloader habis waktu. Coba lagi nanti."
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}") # Untuk debugging di log Vercel
        return None, "Terjadi kesalahan saat menghubungi layanan downloader."

# --- Routing Aplikasi Flask yang Diperbarui ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_input = request.form.get('tiktok_url')
        if not url_input:
            return render_template_string(HTML_TEMPLATE, error="URL tidak boleh kosong.")
        
        # Panggil fungsi backend untuk mendapatkan link dan pesan error
        link, error_message = get_download_link(url_input)
        
        if link:
            # Jika berhasil, tampilkan link download
            return render_template_string(HTML_TEMPLATE, download_link=link)
        else:
            # Jika gagal, tampilkan pesan error yang lebih spesifik
            return render_template_string(HTML_TEMPLATE, error=error_message)
    
    # Tampilan awal saat halaman dibuka
    return render_template_string(HTML_TEMPLATE)

