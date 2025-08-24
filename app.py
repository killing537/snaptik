from flask import Flask, request, render_template_string
import requests
import datetime

app = Flask(__name__)

# --- Template HTML tidak berubah ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader Debug</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 1rem; box-sizing: border-box; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 500px; width: 100%; }
        h1 { font-size: 1.5rem; color: #1877f2; }
        p.subtitle { color: #606770; margin-bottom: 1.5rem; }
        input[type="text"] { width: 100%; padding: 12px; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; box-sizing: border-box; }
        button { background-color: #1877f2; color: white; padding: 12px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; font-weight: bold; width: 100%; transition: background-color 0.2s; }
        button:hover { background-color: #166fe5; }
        .result { margin-top: 1.5rem; }
        .error { color: #f02849; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>TikTok Downloader Debug</h1>
        <form method="post"><input type="text" name="tiktok_url" placeholder="Tempel URL TikTok di sini..." required><button type="submit">Download</button></form>
        <div class="result">{% if error %}<p class="error">Error: {{ error }}</p>{% endif %}</div>
    </div>
</body>
</html>
"""

# --- Fungsi Backend dengan BANYAK PRINT() ---
def get_download_link_from_api(tiktok_url):
    print(f"[{datetime.datetime.now()}] --- FUNGSI DIMULAI ---")
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    try:
        print(f"[{datetime.datetime.now()}] Langkah 1: Mencoba mengubah URL singkat...")
        res = session.head(tiktok_url, headers=headers, allow_redirects=True, timeout=8)
        full_url = res.url
        print(f"[{datetime.datetime.now()}] Langkah 1 SELESAI. URL Panjang: {full_url}")

        api_url = "https://lovetik.com/api/ajax/search"
        data = {'query': full_url}
        
        print(f"[{datetime.datetime.now()}] Langkah 2: Mengirim request ke API lovetik...")
        response = session.post(api_url, headers=headers, data=data, timeout=8)
        print(f"[{datetime.datetime.now()}] Langkah 2 SELESAI. Status code: {response.status_code}")
        
        response.raise_for_status()
        
        print(f"[{datetime.datetime.now()}] Langkah 3: Mencoba membaca JSON...")
        json_data = response.json()
        print(f"[{datetime.datetime.now()}] Langkah 3 SELESAI.")

        if json_data.get('status') == 'ok' and json_data.get('links'):
            for link in json_data['links']:
                if link.get('t') == 'Nowatermark':
                    print(f"[{datetime.datetime.now()}] --- FUNGSI BERHASIL ---")
                    return link.get('u'), None
            return json_data['links'][0].get('u'), None
        else:
            error_message = json_data.get('mess', 'Status bukan OK atau tidak ada links.')
            print(f"[{datetime.datetime.now()}] --- FUNGSI GAGAL: {error_message} ---")
            return None, error_message

    except Exception as e:
        error_message = f"Terjadi EXCEPTION: {str(e)}"
        print(f"[{datetime.datetime.now()}] --- FUNGSI CRASH: {error_message} ---")
        return None, error_message

# --- Routing Aplikasi Flask ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url_input = request.form.get('tiktok_url')
        link, error = get_download_link_from_api(url_input)
        
        if link:
            # Jika berhasil, tidak perlu tampilkan apa-apa, cukup kembalikan halaman biasa
             return render_template_string(HTML_TEMPLATE) # Seharusnya redirect ke link, tapi ini cukup
        else:
            return render_template_string(HTML_TEMPLATE, error=error)
    
    return render_template_string(HTML_TEMPLATE)
        
