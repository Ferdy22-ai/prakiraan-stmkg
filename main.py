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
output_dir = r"D:\STMKG\Prakiraan_Cuaca_STMKG"
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


from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os

# ==== Baca file CSV ====
file_path = r"D:\STMKG\Prakiraan_Cuaca_STMKG\prakiraan_cuaca.csv"
df = pd.read_csv(file_path)
print("Kolom di file:", df.columns.tolist())

# ==== Fungsi ambil nilai ====
def ambil_nilai(df, baris, kolom):
    try:
        nilai = df.iloc[baris][kolom]
        if pd.isna(nilai):
            return ""
        return str(nilai).strip()
    except:
        return ""

# ==== Fungsi paste ikon arah angin (centered & tidak dibulatkan) ====
def paste_rotated_icon(base_img, icon_path, center_position, angle):
    if os.path.exists(icon_path):
        ikon_img = Image.open(icon_path).convert("RGBA").resize((50, 50))

        # Rotasi ikon dengan pusat di tengah
        ikon_img_rotated = ikon_img.rotate(-angle, expand=True)

        # Hitung koordinat untuk penempatan supaya tetap center
        icon_w, icon_h = ikon_img_rotated.size
        center_x, center_y = center_position
        paste_x = center_x - icon_w // 2
        paste_y = center_y - icon_h // 2

        base_img.paste(ikon_img_rotated, (paste_x, paste_y), ikon_img_rotated)
    else:
        print(f"⚠️ Ikon arah tidak ditemukan: {icon_path}")

# ==== Fungsi paste ikon cuaca ====
def paste_ikon_cuaca(base_img, ikon_dir, position, ikon_filename, default_width=100):
    ikon_filename = os.path.splitext(ikon_filename)[0] + ".png"
    ikon_path = os.path.join(ikon_dir, ikon_filename)

    if os.path.exists(ikon_path):
        ikon_img = Image.open(ikon_path).convert("RGBA")

        if "hujan" in ikon_filename.lower():
            target_width = 130
            offset_x = -15
            offset_y = -10
        else:
            target_width = default_width
            offset_x = 0
            offset_y = 0

        scale_ratio = target_width / ikon_img.width
        target_height = int(ikon_img.height * scale_ratio)
        ikon_img = ikon_img.resize((target_width, target_height), Image.LANCZOS)

        x, y = position
        base_img.paste(ikon_img, (x + offset_x, y + offset_y), ikon_img)
    else:
        print(f"⚠️ Ikon cuaca tidak ditemukan: {ikon_path}")

# ==== Siapkan gambar & font ====
template_path = r"D:\STMKG\Prakiraan_Cuaca_STMKG\3.png"
img = Image.open(template_path).convert("RGBA")
draw = ImageDraw.Draw(img)

font_path = "C:/Windows/Fonts/Bahnschrift.ttf"
font = ImageFont.truetype(font_path, 34)

ikon_dir = r"D:\STMKG\Prakiraan_Cuaca_STMKG\ikon_cuaca"
ikon_arah_path = os.path.join(ikon_dir, "ikon_arah_angin.png")

# ==== Data posisi ====
data = [
    {"x": 150, "y": 390, "cell": (0, "Tanggal")},
    {"x": 350, "y": 390, "cell": (0, "Jam")},
    {"x": 730, "y": 390, "cell": (8, "Tanggal")},
    {"x": 930, "y": 390, "cell": (8, "Jam")},
    {"x": 450, "y": 795, "cell": (0, "Suhu (°C)")},
    {"x": 450, "y": 895, "cell": (1, "Suhu (°C)")},
    {"x": 450, "y": 990, "cell": (2, "Suhu (°C)")},
    {"x": 450, "y": 1090, "cell": (3, "Suhu (°C)")},
    {"x": 450, "y": 1185, "cell": (4, "Suhu (°C)")},
    {"x": 450, "y": 1285, "cell": (5, "Suhu (°C)")},
    {"x": 450, "y": 1380, "cell": (6, "Suhu (°C)")},
    {"x": 450, "y": 1480, "cell": (7, "Suhu (°C)")},
    {"x": 620, "y": 795, "cell": (0, "Kelembapan (%)")},
    {"x": 620, "y": 895, "cell": (1, "Kelembapan (%)")},
    {"x": 620, "y": 990, "cell": (2, "Kelembapan (%)")},
    {"x": 620, "y": 1090, "cell": (3, "Kelembapan (%)")},
    {"x": 620, "y": 1185, "cell": (4, "Kelembapan (%)")},
    {"x": 620, "y": 1285, "cell": (5, "Kelembapan (%)")},
    {"x": 620, "y": 1380, "cell": (6, "Kelembapan (%)")},
    {"x": 620, "y": 1480, "cell": (7, "Kelembapan (%)")},
    {"x": 850, "y": 795, "cell": (0, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 892, "cell": (1, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 992, "cell": (2, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 1087, "cell": (3, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 1187, "cell": (4, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 1285, "cell": (5, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 1380, "cell": (6, "Kecepatan Angin (knots)")},
    {"x": 850, "y": 1480, "cell": (7, "Kecepatan Angin (knots)")},
    {"x": 320, "y": 780, "cell": (0, "File Ikon")},
    {"x": 320, "y": 867, "cell": (1, "File Ikon")},
    {"x": 320, "y": 967, "cell": (2, "File Ikon")},
    {"x": 320, "y": 1065, "cell": (3, "File Ikon")},
    {"x": 320, "y": 1165, "cell": (4, "File Ikon")},
    {"x": 320, "y": 1265, "cell": (5, "File Ikon")},
    {"x": 320, "y": 1358, "cell": (6, "File Ikon")},
    {"x": 320, "y": 1456, "cell": (7, "File Ikon")},
]

# ==== Plot ====
for item in data:
    x = item["x"]
    y = item["y"]
    baris, kolom = item["cell"]
    teks = ambil_nilai(df, baris, kolom)

    if "File Ikon" not in kolom:
        draw.text((x, y), teks, font=font, fill="white")

    if "Kecepatan Angin" in kolom:
        arah_angin = ambil_nilai(df, baris, "Arah Angin (°)")
        try:
            angle = float(arah_angin)  # ✅ Tidak dibulatkan
            paste_rotated_icon(img, ikon_arah_path, (x - 60, y + 20), angle)  # ✅ Posisi ikon tengah
        except:
            print(f"⚠️ Arah angin tidak valid di baris {baris}: {arah_angin}")

    if "File Ikon" in kolom:
        paste_ikon_cuaca(img, ikon_dir, (x, y), teks)

# ==== Simpan ====
output_path = r"D:\STMKG\Prakiraan_Cuaca_STMKG\prakiraan_terisi.png"
img.save(output_path)
print(f"✅ Gambar prakiraan selesai: {output_path}")

import smtplib
from email.message import EmailMessage

# Buat email
msg = EmailMessage()
msg['Subject'] = '📡 Prakiraan Cuaca Harian STMKG'
msg['From'] = 'ferdyindra38@@gmail.com'
msg['To'] = 'ferdyindra586l@gmail.com'
msg.set_content('Berikut adalah gambar prakiraan cuaca yang telah dibuat secara otomatis.')

# Baca dan attach gambar
with open("/home/ferdy/prakiraan/prakiraan_terisi.png", "rb") as f:
    file_data = f.read()
    file_name = "prakiraan_terisi.png"
    msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

# Kirim email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login('your_email@gmail.com', 'tnna udpl fsjo eoge')  # App password, bukan password biasa
    smtp.send_message(msg)

print("✅ Email berhasil dikirim!")
