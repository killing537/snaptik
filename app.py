from flask import Flask, request, render_template_string
import requests

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# --- Template HTML disatukan di sini agar mudah ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader Final</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 1rem; box-sizing: border-box; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 100%; }
        h1 { font-size: 1.5rem; color: #1877f2; }
        p.subtitle { color: #606770; margin-bottom: 1.5rem; }
        input[type="text"] { width: 100%; padding: 12px; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; box-sizing: border-box; }
        button { background-color: #1877f2; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: bold; width: 100%; transition: background-color 0.2s; }
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
        <h1>TikTok Downloader Final</h1>
        <p class="subtitle">Mendukung semua format URL.</p>
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

# --- Fungsi Backend Final dengan Penanganan URL Singkat ---
def get_download_link_from_api(tiktok_url):
    session = requests.Session()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        # Langkah 1: Ubah URL singkat (vt.tiktok.com) menjadi URL panjang.
        res = session.head(tiktok_url, headers=headers, allow_redirects=True, timeout=10)
        full_url = res.url # Ini akan berisi URL final setelah semua pengalihan

        # Langkah 2: Kirim URL PANJANG ke API lovetik.com
        api_url = "https://lovetik.com/api/ajax/search"
        data = {'query': full_url} # Gunakan full_url di sini
        response = session.post(api_url, headers=headers, data=data, timeout=20)
        response.raise_for_status()
        
        json_data = response.json()

        if json_data.get('status') == 'ok' and json_data.get('links'):
            for link in json_data['links']:
                if link.get('t') == 'Nowatermark':
                    return link.get('u'), None
            return json_data['links'][0].get('u'), None
        else:
            error_message = json_data.get('mess', 'Gagal memproses video. URL mungkin tidak valid atau video bersifat privat.')
            return None, error_message

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return None, "Terjadi kesalahan saat menghubungi API downloader."
    except ValueError:
        return None, "Gagal membaca respons dari API. Mungkin layanan sedang down."

# --- Routing Aplikasi Flask ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_input = request.form.get('tiktok_url')
        if not url_input:
            return render_template_string(HTML_TEMPLATE, error="URL tidak boleh kosong.")
        
        link, error = get_download_link_from_api(url_input)
        
        if link:
            return render_template_string(HTML_TEMPLATE, download_link=link)
        else:
            return render_template_string(HTML_TEMPLATE, error=error)
    
    return render_template_string(HTML_TEMPLATE)
                                          
