import requests
import csv
import os

# URL API BMKG
url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=36.71.01.1003"

# Tambahkan User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Ambil data
response = requests.get(url, headers=headers)
data = response.json()
print(data)
