import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.ports.publisher_service import PublisherService
from core.entities.post import Post

class SeleniumFacebookDriver(PublisherService):
    def __init__(self, session_path: str = "facebook_session"):
        self.driver = None
        self.session_path = os.path.abspath(session_path)

    def get_name(self) -> str:
        return "Facebook"

    def start_service(self):
        if self.driver: return
        print("🔵 FB: Iniciando Navegador...")
        
        options = Options()
        options.add_argument(f"user-data-dir={self.session_path}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            print("🌍 FB: Entrando a Facebook...")
            self.driver.get("https://www.facebook.com")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error iniciando FB: {e}")
            raise e

    def stop_service(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def ensure_connection(self):
        if not self.driver:
            self.start_service()

    def upload_status(self, post: Post):
        self.ensure_connection()
        print(f"🔵 FB: Subiendo Historia...")
        
        try:
            # 1. URL DIRECTA
            self.driver.get("https://www.facebook.com/stories/create")
            time.sleep(4)

            # 2. INYECTAR FOTO
            print("🔵 FB: Inyectando archivo...")
            file_inputs = self.driver.find_elements(By.XPATH, '//input[@type="file"]')
            if not file_inputs:
                raise Exception("No encontré el input de carga.")
            
            target_input = file_inputs[-1]
            self.driver.execute_script("arguments[0].style.display = 'block';", target_input)
            target_input.send_keys(post.image_path)
            
            print("⏳ FB: Procesando imagen (5s)...")
            time.sleep(5) 

            # 3. PUBLICAR (Directo, sin zoom, sin editar)
            print("🔵 FB: Publicando...")
            xpath_share = '//span[contains(text(), "Compartir en historia")]'
            
            btn_share = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_share))
            )
            self.driver.execute_script("arguments[0].click();", btn_share)
            
            print("✅ FB: ¡HISTORIA ENVIADA!")
            time.sleep(5)

        except Exception as e:
            print(f"🔥 Error en Facebook: {e}")
            self.driver.save_screenshot("error_fb_upload.png")
            raise e