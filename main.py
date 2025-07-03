import os
import csv
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib

# === Setup direktori ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, "output")
icon_dir = os.path.join(BASE_DIR, "ikon_cuaca")
template_path = os.path.join(BASE_DIR, "3.png")
font_path = os.path.join(BASE_DIR, "BAHNSCHRIFT 1.TTF")
csv_path = os.path.join(output_dir, "prakiraan_cuaca.csv")
img_path = os.path.join(output_dir, "prakiraan_terisi.png")
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

def ambil(df, row, col):
    val = df.iloc[row][col]
    return str(val) if not pd.isna(val) else ""

def paste_rotated_icon(base_img, icon_path, center, angle):
    if os.path.exists(icon_path):
        ikon = Image.open(icon_path).convert("RGBA").resize((50, 50))
        rotated = ikon.rotate(-float(angle), expand=True)
        w, h = rotated.size
        x, y = center
        base_img.paste(rotated, (x - w // 2, y - h // 2), rotated)

def paste_ikon_cuaca(base_img, ikon_dir, pos, filename):
    path = os.path.join(ikon_dir, os.path.splitext(filename)[0] + ".png")
    if os.path.exists(path):
        ikon = Image.open(path).convert("RGBA")
        scale = 130 if "hujan" in filename.lower() else 100
        ikon = ikon.resize((scale, int(ikon.height * scale / ikon.width)), Image.LANCZOS)
        base_img.paste(ikon, pos, ikon)

positions = [(0, "Tanggal", 150, 390), (0, "Jam", 350, 390), (8, "Tanggal", 730, 390), (8, "Jam", 930, 390)]
for i in range(8):
    positions += [
        (i, "Suhu (°C)", 450, 795 + i * 95),
        (i, "Kelembapan (%)", 620, 795 + i * 95),
        (i, "Kecepatan Angin (knots)", 850, 795 + i * 95),
        (i, "File Ikon", 320, 780 + i * 95)
    ]

for row, col, x, y in positions:
    teks = ambil(df, row, col)
    if "File Ikon" not in col:
        draw.text((x, y), teks, font=font, fill="white")
    elif "Kecepatan Angin" in col:
        arah = ambil(df, row, "Arah Angin (°)")
        paste_rotated_icon(img, ikon_arah_path, (x - 60, y + 20), arah)
    else:
        paste_ikon_cuaca(img, icon_dir, (x, y), teks)

img.save(img_path)
print(f"✅ Gambar disimpan di: {img_path}")

# === Kirim Email ===
EMAIL_ADDRESS = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

msg = EmailMessage()
msg['Subject'] = 'Prakiraan Cuaca Harian STMKG'
msg['From'] = EMAIL_ADDRESS
msg['To'] = 'ferdyindra586@gmail.com'
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

print("✅ Email beserta CSV dan gambar berhasil dikirim.")
