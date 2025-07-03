import os
import csv
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from email.message import EmailMessage
import smtplib

# Direktori output
output_dir = "./output"
icon_dir = os.path.join(output_dir, "ikon_cuaca")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(icon_dir, exist_ok=True)

# URL API BMKG
url = "url = "https://prakiraan-stmkg.onrender.com/bmkg"
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# Ambil data
response = requests.get(url, headers=headers)
data = response.json()

# Fungsi konversi
def kmh_to_knots(kmh):
    try:
        return f"{float(kmh) * 0.539957:.1f}"
    except:
        return ""

# Simpan CSV
csv_path = os.path.join(output_dir, "prakiraan_cuaca.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tanggal", "Jam", "Cuaca", "Suhu (\u00b0C)", "Kelembapan (%)", "Kecepatan Angin (km/j)", "Kecepatan Angin (knots)", "Arah Angin (\u00b0)", "File Ikon"])

    for group in data["data"][0]["cuaca"]:
        for item in group:
            dt = item.get("local_datetime", "")
            Tanggal, jam = dt[:10], dt[11:16]
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

            writer.writerow([Tanggal, jam, cuaca, suhu, kelembapan, angin, angin_knots, arah_angin, ikon_filename])

# ==== Visualisasi ke PNG ====
df = pd.read_csv(csv_path)
img = Image.open("3.png").convert("RGBA")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("BAHNSCHRIFT 1.TTF", 34)

ikon_arah_path = os.path.join("ikon_cuaca", "ikon_arah_angin.png")

# Fungsi ambil nilai
ambil = lambda row, col: str(df.iloc[row][col]) if not pd.isna(df.iloc[row][col]) else ""

# Fungsi paste ikon arah
def paste_rotated_icon(base_img, icon_path, center, angle):
    if os.path.exists(icon_path):
        ikon = Image.open(icon_path).convert("RGBA").resize((50, 50))
        rotated = ikon.rotate(-float(angle), expand=True)
        w, h = rotated.size
        x, y = center
        base_img.paste(rotated, (x - w // 2, y - h // 2), rotated)

# Fungsi paste ikon cuaca
def paste_ikon_cuaca(base_img, ikon_dir, pos, filename):
    path = os.path.join(ikon_dir, os.path.splitext(filename)[0] + ".png")
    if os.path.exists(path):
        ikon = Image.open(path).convert("RGBA")
        scale = 130 if "hujan" in filename.lower() else 100
        ikon = ikon.resize((scale, int(ikon.height * scale / ikon.width)), Image.LANCZOS)
        base_img.paste(ikon, pos, ikon)

# Gambar
positions = [(0, "Tanggal", 150, 390), (0, "Jam", 350, 390), (8, "Tanggal", 730, 390), (8, "Jam", 930, 390)]
for i in range(8):
    positions += [
        (i, "Suhu (\u00b0C)", 450, 795 + i * 95),
        (i, "Kelembapan (%)", 620, 795 + i * 95),
        (i, "Kecepatan Angin (knots)", 850, 795 + i * 95),
        (i, "File Ikon", 320, 780 + i * 95)
    ]

for row, col, x, y in positions:
    teks = ambil(row, col)
    if "File Ikon" not in col:
        draw.text((x, y), teks, font=font, fill="white")
    elif "Kecepatan Angin" in col:
        arah = ambil(row, "Arah Angin (\u00b0)")
        paste_rotated_icon(img, ikon_arah_path, (x - 60, y + 20), arah)
    else:
        paste_ikon_cuaca(img, icon_dir, (x, y), teks)

# Simpan gambar
img_path = os.path.join(output_dir, "prakiraan_terisi.png")
img.save(img_path)

# ==== Kirim email ====
email_address = os.environ['EMAIL_ADDRESS']
email_password = os.environ['EMAIL_PASSWORD']

msg = EmailMessage()
msg['Subject'] = 'Prakiraan Cuaca Harian STMKG'
msg['From'] = email_address
msg['To'] = 'ferdyindra586@gmail.com'
msg.set_content('Berikut prakiraan cuaca hari ini.')

with open(img_path, "rb") as f:
    msg.add_attachment(f.read(), maintype='image', subtype='png', filename='prakiraan_terisi.png')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(email_address, email_password)
    smtp.send_message(msg)

print("✅ Email terkirim.")
