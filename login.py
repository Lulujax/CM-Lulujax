# login.py
# Ejecuta esto SOLO UNA VEZ para escanear el código QR.
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def login():
    print("🔓 Iniciando modo de registro de sesión...")
    
    # Configuración base
    options = Options()
    
    # IMPORTANTE: Usamos la misma carpeta de sesión que usa el bot principal
    # Así, lo que escanees aquí, quedará guardado para el otro script.
    dir_path = os.getcwd()
    profile_path = os.path.join(dir_path, "whatsapp_session")
    options.add_argument(f"user-data-dir={profile_path}")
    
    # Iniciamos Chrome NORMAL (Sin emulación móvil)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get("https://web.whatsapp.com")
    
    print("📸 POR FAVOR, ESCANEA EL CÓDIGO QR AHORA.")
    print("⏳ Tienes 60 segundos antes de que se cierre...")
    print("NOTA: Espera a que carguen tus chats antes de que se cierre.")
    
    time.sleep(60)
    driver.quit()

if __name__ == "__main__":
    login()