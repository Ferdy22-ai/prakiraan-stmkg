#====================================================================================================================#
#                                               Script Created By Penelitian ITMK 2022 K                             #
#====================================================================================================================#


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

# Buat folder output
output_dir = r"D:\STMKG\Semester_6\Prakiraan_Cuaca_STMKG"
icon_dir = os.path.join(output_dir, "ikon_cuaca")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(icon_dir, exist_ok=True)

# Fungsi konversi km/j ke knots
def kmh_to_knots(kmh):
    try:
        kmh_float = float(kmh)
        knots = kmh_float * 0.539957
        return f"{knots:.1f}"  # hanya angka 1 desimal
    except:
        return ""

# Path file CSV
csv_path = os.path.join(output_dir, "prakiraan_cuaca.csv")

# Siapkan file CSV
with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    
    # Header
    writer.writerow([
        "Tanggal", "Jam", "Cuaca",
        "Suhu (°C)", "Kelembapan (%)",
        "Kecepatan Angin (km/j)", "Kecepatan Angin (knots)", 
        "Arah Angin (°)", "File Ikon"
    ])
    
    # Isi data
    for group in data["data"][0]["cuaca"]:
        for item in group:
            datetime_str = item.get("local_datetime", "")
            Tanggal = ""
            jam = ""
            if len(datetime_str) >= 16:
                Tanggal = datetime_str[0:10]  # yyyy-mm-dd
                jam = datetime_str[11:16]     # HH:MM

            cuaca = item.get("weather_desc", "")
            suhu = item.get("t", "")
            kelembapan = item.get("hu", "")
            angin = item.get("ws", "")
            arah_angin = item.get("wd_deg", "")  # ambil wd_deg dari API
            angin_knots = kmh_to_knots(angin)

            ikon_url = item.get("image", "")
            ikon_filename = ""
            if ikon_url:
                ikon_filename = ikon_url.split("/")[-1]
                ikon_path = os.path.join(icon_dir, ikon_filename)

                # Download ikon jika belum ada
                if not os.path.exists(ikon_path):
                    try:
                        ikon_response = requests.get(ikon_url)
                        with open(ikon_path, "wb") as f:
                            f.write(ikon_response.content)
                        print(f"✅ Ikon disimpan: {ikon_path}")
                    except Exception as e:
                        print(f"⚠️ Gagal download ikon {ikon_filename}: {e}")

            writer.writerow([
                Tanggal, jam, cuaca, suhu, kelembapan, 
                angin, angin_knots, arah_angin, ikon_filename
            ])

print(f"✅ File prakiraan_cuaca.csv berhasil dibuat di: {csv_path}")
