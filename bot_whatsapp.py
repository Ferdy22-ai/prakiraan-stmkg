from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pyperclip
import os

# === KONFIGURASI ===
CHROMEDRIVER_PATH = "D:/STMKG/Prakiraan_Cuaca_STMKG/chromedriver.exe"
USER_DATA_DIR = "D:/STMKG/Prakiraan_Cuaca_STMKG/chrome_profile"
KONTAK = "ITM PERIODE 2025"
GAMBAR_PATH = "D:/STMKG/Prakiraan_Cuaca_STMKG/prakiraan_terisi.png"
CAPTION = "📍 Prakiraan Cuaca Hari Ini\n🤖 Semoga harimu cerah dan menyenangkan!"

# === SETUP SELENIUM DENGAN PROFIL CHROME YANG SUDAH LOGIN ===
options = Options()
options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
options.add_argument("--profile-directory=Default")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)
driver.get("https://web.whatsapp.com")

print("⌛ Menunggu login WhatsApp Web (15 detik)...")
time.sleep(15)

try:
    # === CARI KONTAK ===
    print(f"🔍 Mencari kontak: {KONTAK}")
    search_box = driver.find_element(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
    search_box.click()
    time.sleep(1)
    search_box.send_keys(KONTAK)
    time.sleep(2)
    driver.find_element(By.XPATH, f"//span[@title='{KONTAK}']").click()
    time.sleep(2)

    # === KLIK IKON LAMPIRAN ===
    print("📎 Klik ikon lampiran...")
    attachment_xpath = "/html/body/div[1]/div/div/div[3]/div/div[4]/div/footer/div[1]/div/span/div/div[2]/div/div[1]/button/span"
    attachment_btn = driver.find_element(By.XPATH, attachment_xpath)
    attachment_btn.click()
    time.sleep(1)

    # === PILIH INPUT FILE DAN UPLOAD GAMBAR ===
    print("🖼️ Upload gambar...")
    input_file = driver.find_element(By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']")
    input_file.send_keys(GAMBAR_PATH)
    time.sleep(3)

    # === MASUKKAN CAPTION MENGGUNAKAN CLIPBOARD ===
    print("💬 Menambahkan caption (clipboard)...")
    caption_xpath = "/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/p"
    caption_box = driver.find_element(By.XPATH, caption_xpath)
    caption_box.click()
    pyperclip.copy(CAPTION)
    caption_box.send_keys(Keys.CONTROL, 'v')
    time.sleep(2)

    # === KLIK TOMBOL KIRIM ===
    print("📤 Mengirim gambar...")
    send_button_xpath = "/html/body/div[1]/div/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div/span"
    driver.find_element(By.XPATH, send_button_xpath).click()

    print("✅ Gambar dan caption berhasil dikirim ke:", KONTAK)

except Exception as e:
    print("❌ Terjadi kesalahan:", e)
