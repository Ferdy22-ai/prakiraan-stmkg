import requests
import csv
import os

# URL API BMKG
url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=36.71.01.1003"

# Tambahkan User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Ambil data dengan header
response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Content: {response.text[:500]}") # Cetak 500 karakter pertama

if response.status_code == 200:
    try:
        data = response.json()
        print("Data berhasil diuraikan sebagai JSON.")
        # Lanjutkan pemrosesan data di sini
        # Contoh: print(data.keys())
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error saat menguraikan JSON: {e}")
        print("Mungkin respons bukan JSON yang valid meskipun status 200.")
else:
    print(f"Gagal mengambil data. Status code: {response.status_code}")
    print(f"Isi respons: {response.text}")
    