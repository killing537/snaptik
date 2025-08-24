import requests
import re

def fetch_and_find_token(url):
    """
    Fungsi ini berfungsi seperti cURL: mengambil konten URL
    dan mencoba mencari token di dalamnya.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    print(f"[*] Mencoba mengambil konten dari: {url}\n")

    try:
        # Mengirim permintaan GET untuk mendapatkan HTML mentah
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Cek jika ada error HTTP seperti 404 atau 500
        html_content = response.text

        print("[+] Konten HTML berhasil diunduh.")
        
        # Mencari pola input token di dalam HTML yang didapat
        # Pola: <input ... name="token" value="NILAI_TOKEN" ... >
        token_search = re.search(r'<input[^>]+name="token"[^>]+value="([^"]+)"', html_content)

        print("\n--- HASIL PENCARIAN TOKEN ---")
        if token_search and token_search.group(1):
            # Jika token ditemukan DAN nilainya tidak kosong
            token = token_search.group(1)
            print(f"✅ Token DITEMUKAN!")
            print(f"   Nilai Token: {token}")
        else:
            # Jika token tidak ditemukan ATAU nilainya kosong (value="")
            print(f"❌ Token TIDAK DITEMUKAN.")
            print("   Ini membuktikan token ditambahkan oleh JavaScript setelah halaman dimuat.")

        # Menampilkan potongan HTML di sekitar form untuk bukti
        print("\n--- Potongan HTML di Sekitar Form ---")
        form_search = re.search(r'(<form[^>]+form-url[^>]+>.*?</form>)', html_content, re.DOTALL)
        if form_search:
            print(form_search.group(1).strip())
        else:
            print("Form utama tidak ditemukan di dalam HTML.")

    except requests.exceptions.RequestException as e:
        print(f"[!] Gagal melakukan permintaan: {e}")

# --- Bagian Eksekusi Skrip ---
if __name__ == "__main__":
    target_url = "https://snaptik.app/ID2"
    fetch_and_find_token(target_url)

