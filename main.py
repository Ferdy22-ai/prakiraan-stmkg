import os
import csv
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib
from datetime import datetime
  
# Dapatkan tanggal sekarang
tanggal_sekarang = datetime.now().strftime("%d-%B-%Y")  # contoh: 12-Juli-2025

# Nama file berdasarkan tanggal
nama_csv = f"Prakiraan Cuaca STMKG {tanggal_sekarang}.csv"
nama_png = f"Prakiraan Cuaca STMKG {tanggal_sekarang}.png"
 
# === Setup direktori ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, "output")
icon_dir = os.path.join(BASE_DIR, "ikon_cuaca")
template_path = os.path.join(BASE_DIR, "3.png")
font_path = os.path.join(BASE_DIR, "BAHNSCHRIFT 1.TTF")
csv_path = os.path.join(output_dir, nama_csv)
img_path = os.path.join(output_dir, nama_png)
ikon_arah_path = os.path.join(icon_dir, "ikon_arah_angin.png")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(icon_dir, exist_ok=True)

# URL API BMKG
url = "https://api.bmkg.go.id/publik/prakiraan-cuaca?adm4=36.71.01.1003"

# Tambahkan User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Ambil data
response = requests.get(url, headers=headers)
data = response.json()

# === Konversi km/h ke knots ===
def kmh_to_knots(kmh):
    try:
        return f"{float(kmh) * 0.539957:.1f}"
    except:
        return ""

# === Simpan CSV ===
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tanggal", "Jam", "Cuaca", "Suhu (°C)", "Kelembapan (%)", "Kecepatan Angin (km/j)", "Kecepatan Angin (knots)", "Arah Angin (°)", "File Ikon"])

    for group in data["data"][0]["cuaca"]:
        for item in group:
            dt = item.get("local_datetime", "")
            tanggal, jam = dt[:10], dt[11:16]
            cuaca = item.get("weather_desc", "")
            suhu = item.get("t", "")
            kelembapan = item.get("hu", "")
            angin = item.get("ws", "")
            arah_angin = item.get("wd_deg", "")
            angin_knots = kmh_to_knots(angin)
            ikon_url = item.get("image", "")
            ikon_filename = ikon_url.split("/")[-1] if ikon_url else ""

            if ikon_url:
                ikon_path = os.path.join(icon_dir, ikon_filename)
                if not os.path.exists(ikon_path):
                    try:
                        r = requests.get(ikon_url)
                        with open(ikon_path, "wb") as img_file:
                            img_file.write(r.content)
                    except:
                        pass

            writer.writerow([tanggal, jam, cuaca, suhu, kelembapan, angin, angin_knots, arah_angin, ikon_filename])

# === Visualisasi ke PNG ===
df = pd.read_csv(csv_path)
img = Image.open(template_path).convert("RGBA")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype(font_path, 34)

# ==== Fungsi ambil nilai ====
def ambil_nilai(df, baris, kolom):
    try:
        nilai = df.iloc[baris][kolom]
        if pd.isna(nilai):
            return ""
        return str(nilai).strip()
    except:
        return ""

# ==== Fungsi paste ikon arah angin ====
def paste_rotated_icon(base_img, icon_path, center_position, angle):
    if os.path.exists(icon_path):
        ikon_img = Image.open(icon_path).convert("RGBA").resize((50, 50))
        ikon_img_rotated = ikon_img.rotate(-float(angle), expand=True)
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

# ==== Tempelkan semua data ke gambar ====
for item in data:
    x, y = item["x"], item["y"]
    baris, kolom = item["cell"]
    nilai = ambil_nilai(df, baris, kolom)

    if "File Ikon" in kolom:
        paste_ikon_cuaca(img, icon_dir, (x, y), nilai)

    elif "Kecepatan Angin" in kolom:
        arah = ambil_nilai(df, baris, "Arah Angin (°)")
        try:
            paste_rotated_icon(img, ikon_arah_path, (x - 60, y + 20), float(arah))
        except:
            print(f"⚠️ Gagal menempelkan ikon arah angin di baris {baris}")
        # Tampilkan angka kecepatan angin juga
        draw.text((x, y), nilai, font=font, fill="white")

    else:
        draw.text((x, y), nilai, font=font, fill="white")


img.save(img_path)
print(f"✅ Gambar disimpan di: {img_path}")

# === Kirim Email ===
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

msg = EmailMessage()
msg['Subject'] = 'Prakiraan Cuaca Harian STMKG'
msg['From'] = EMAIL_ADDRESS
msg['To'] = ', '.join(['bayufirdanan@gmail.com', 'ashamadnusriah@gmail.com'])
msg.set_content('Berikut prakiraan cuaca hari ini dalam format gambar dan CSV.')

# Lampirkan gambar
with open(img_path, "rb") as f_img:
    msg.add_attachment(f_img.read(), maintype='image', subtype='png', filename='prakiraan_terisi.png')

# Lampirkan CSV
with open(csv_path, "rb") as f_csv:
    msg.add_attachment(f_csv.read(), maintype='text', subtype='csv', filename='prakiraan_cuaca.csv')

# Kirim email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("✅ Email beserta CSV dan gambar berhasil dikirim ke semua penerima.")
