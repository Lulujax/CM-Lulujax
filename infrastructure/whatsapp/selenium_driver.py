import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Importamos el nuevo contrato
from core.ports.publisher_service import PublisherService
from core.entities.post import Post

class SeleniumWhatsAppDriver(PublisherService):
    def __init__(self, session_path: str = "whatsapp_session"):
        self.driver = None
        self.session_path = os.path.abspath(session_path)

    def get_name(self) -> str:
        return "WhatsApp"

    def start_service(self):
        if self.driver:
            return

        print("🚀 Iniciando WhatsApp Driver...")
        options = Options()
        options.add_argument(f"user-data-dir={self.session_path}")
        options.add_argument("--start-maximized")
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        
        # Ajusta ruta si es necesario según tu instalación
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("🌍 Navegando a WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            self._wait_for_login()
        except Exception as e:
            print(f"❌ Error al iniciar WA: {e}")
            if self.driver:
                self.driver.quit()
                self.driver = None
            raise e

    def _wait_for_login(self):
        print("⏳ WA: Verificando sesión...")
        try:
            WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.ID, "pane-side"))
            )
            print("✅ WA: ¡Sesión lista!")
        except:
            raise Exception("WA: Tiempo agotado. No iniciaste sesión.")

    def ensure_connection(self):
        if not self.driver:
            self.start_service()
        try:
            self.driver.title
        except:
            self.driver = None
            self.start_service()

    def stop_service(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def upload_status(self, post: Post):
        self.ensure_connection()
        print(f"📸 WA: Procesando campaña...")

        try:
            # 1. PESTAÑA ESTADOS
            print("1. WA: Buscando pestaña de Estados...")
            xpath_tab = '//span[@data-icon="status-refreshed"] | //div[@aria-label="Estados"] | //div[@title="Estados"]'
            
            btn_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_tab))
            )
            try:
                btn_tab.click()
            except:
                btn_tab.find_element(By.XPATH, "./..").click()
                
            time.sleep(2)

            # 2. BOTÓN "+"
            print("2. WA: Buscando botón '+'...")
            xpath_plus = '//*[local-name()="svg"]/*[local-name()="title"][text()="ic-add-circle"]/../..'
            
            try:
                btn_plus = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath_plus))
                )
                btn_plus.click()
            except:
                self.driver.find_element(By.XPATH, '//div[contains(text(), "Mi estado")]/..').click()

            # 3. FOTOS Y VIDEOS (PyAutoGUI)
            print("3. WA: Seleccionando 'Fotos y videos'...")
            xpath_option = '//span[contains(text(), "Fotos y videos")] | //span[contains(text(), "Photos and videos")]'
            
            btn_option = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, xpath_option))
            )
            
            btn_option.click() 
            time.sleep(2) 
            
            print("🤖 WA: Escribiendo ruta de imagen...")
            absolute_path = os.path.abspath(post.image_path)
            pyautogui.write(absolute_path)
            time.sleep(1)
            pyautogui.press('enter')
            
            print("✅ WA: Imagen seleccionada.")

            # 4. EDITOR
            print("4. WA: Esperando editor...")
            xpath_caption = '//div[@aria-label="Añade un comentario"] | //div[@aria-placeholder="Añade un comentario"]'
            
            caption_box = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, xpath_caption))
            )

            if post.caption:
                print("✍️ WA: Escribiendo copy...")
                time.sleep(1)
                caption_box.click()
                caption_box.send_keys(post.caption)
                time.sleep(1)

            # 5. ENVIAR
            print("5. WA: Enviando...")
            xpath_send = '//span[@data-icon="wds-ic-send-filled"]'
            
            btn_send = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_send))
            )
            btn_send.click()
            
            print("✅ WA: ¡ESTADO PUBLICADO!")
            time.sleep(4)
            
            try:
                self.driver.find_element(By.XPATH, '//span[@data-icon="chat"]').click()
            except:
                pass

        except Exception as e:
            print(f"🔥 WA Error: {e}")
            raise e