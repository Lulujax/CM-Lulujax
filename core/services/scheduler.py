import time
import threading
from datetime import datetime, timedelta
from typing import Callable, List
from core.entities.post import Post
from core.ports.publisher_service import PublisherService 

class SchedulerService:
    def __init__(self, drivers: List[PublisherService], log_callback: Callable[[str], None]):
        self.drivers = drivers 
        self.log = log_callback

    def schedule_post(self, post: Post, hh: int, mm: int):
        now = datetime.now()
        target_time = now.replace(hour=hh, minute=mm, second=0, microsecond=0)

        if target_time < now:
            target_time += timedelta(days=1)

        wait_seconds = (target_time - now).total_seconds()
        
        self.log(f"📅 Tarea programada para: {target_time.strftime('%H:%M')}")
        self.log(f"⏳ Esperando {int(wait_seconds // 60)} min...")

        # Lanza el hilo que esperará y luego ejecutará
        thread = threading.Thread(target=self._wait_and_execute, args=(wait_seconds, post), daemon=True)
        thread.start()

    def execute_now(self, post: Post):
        self.log("🚀 Iniciando difusión inmediata...")
        # Lanza el hilo que ejecuta YA MISMO
        # Al usar _execute_task, aprovechamos la limpieza automática
        threading.Thread(target=self._execute_task, args=(post,), daemon=True).start()

    def _wait_and_execute(self, seconds, post):
        time.sleep(seconds)
        self.log("⏰ Hora cumplida. Ejecutando difusión...")
        self._execute_task(post)

    def _execute_task(self, post: Post):
        """
        Esta es la función MAESTRA.
        Tanto 'execute_now' como 'schedule_post' terminan aquí.
        Por eso, el bloque 'finally' de limpieza se ejecuta SIEMPRE.
        """
        try:
            for driver in self.drivers:
                try:
                    self.log(f"⚡ Conectando a {driver.get_name()}...")
                    driver.upload_status(post)
                    self.log(f"✅ Éxito en {driver.get_name()}")
                except Exception as e:
                    self.log(f"❌ Falló {driver.get_name()}: {str(e)}")
            
            self.log("🏁 Difusión completada con éxito.")

        finally:
            # --- FASE DE LIMPIEZA (CLEAN UP) ---
            # Este código se ejecuta SIEMPRE, haya error o no, sea programado o inmediato.
            self.log("🧹 Cerrando navegadores y liberando RAM...")
            for driver in self.drivers:
                try:
                    driver.stop_service()
                except Exception:
                    pass 
            self.log("👋 Sistema en reposo. Listo para la próxima.")