from abc import ABC, abstractmethod
from core.entities.post import Post

class PublisherService(ABC):
    """
    Contrato (Interface) que deben cumplir todas las redes sociales.
    Define QUÉ se puede hacer, pero no CÓMO.
    """
    
    @abstractmethod
    def start_service(self):
        """Inicia el navegador y proceso de login"""
        pass

    @abstractmethod
    def stop_service(self):
        """Cierra recursos"""
        pass
    
    @abstractmethod
    def upload_status(self, post: Post):
        """Lógica específica para subir el contenido"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Nombre para mostrar en la interfaz (Ej: 'WhatsApp', 'Facebook')"""
        pass