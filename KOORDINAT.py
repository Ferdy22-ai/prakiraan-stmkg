#====================================================================================================================#
#                                               Script Created By Penelitian ITMK 2022 K                             #
#====================================================================================================================#

import tkinter as tk
from PIL import Image, ImageTk
import csv

# Inisialisasi file CSV
csv_file = "koordinat_klik.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["X", "Y"])  # Header kolom

def on_click(event):
    # Hitung koordinat asli berdasarkan skala
    x_rescaled = int(event.x * img.width / img_resized.width)
    y_rescaled = int(event.y * img.height / img_resized.height)

    result_label.config(text=f"Koordinat Klik:\nX: {x_rescaled} | Y: {y_rescaled}")

    # Simpan ke CSV
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([x_rescaled, y_rescaled])

    print(f"Koordinat disimpan: X={x_rescaled}, Y={y_rescaled}")

# Inisialisasi GUI
root = tk.Tk()
root.title("Klik Gambar untuk Koordinat")

# Muat gambar
image_path = r"C:\Anaconda\envs\Kris\PROJEKMFY\2.png"
img = Image.open(image_path)

# Hitung ukuran jendela layar
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# Hitung skala agar gambar muat di layar (80% dari ukuran layar)
max_w = int(screen_w * 0.8)
max_h = int(screen_h * 0.8)

scale = min(max_w / img.width, max_h / img.height, 1)
new_w = int(img.width * scale)
new_h = int(img.height * scale)

# Resize gambar dengan Pillow versi baru
try:
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
except AttributeError:
    img_resized = img.resize((new_w, new_h), Image.LANCZOS)

photo = ImageTk.PhotoImage(img_resized)

# Label gambar
img_label = tk.Label(root, image=photo)
img_label.pack()

# Bind klik
img_label.bind("<Button-1>", on_click)

# Label hasil koordinat
result_label = tk.Label(root, text="", fg="blue")
result_label.pack()

# Atur ukuran window
root.geometry(f"{new_w}x{new_h + 50}")

root.mainloop()
