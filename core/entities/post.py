import os
from datetime import datetime

class Post:
    def __init__(self, image_path: str, caption: str, schedule_time: datetime):
        # Atributos privados (Encapsulamiento)
        self.__image_path = None
        self.__caption = None
        self.__schedule_time = None

        # Usamos setters para validar al instanciar (Auto-validación)
        self.image_path = image_path
        self.caption = caption
        self.schedule_time = schedule_time

    @property
    def image_path(self) -> str:
        return self.__image_path

    @image_path.setter
    def image_path(self, path: str):
        if not path:
            raise ValueError("La ruta no puede estar vacía.")
        # Validación: El archivo debe existir en el disco
        if not os.path.exists(path):
            raise FileNotFoundError(f"No existe el archivo: {path}")
        self.__image_path = path

    @property
    def caption(self) -> str:
        return self.__caption

    @caption.setter
    def caption(self, text: str):
        # Validación: Límite de caracteres de WhatsApp
        if text and len(text) > 700:
            raise ValueError("El texto excede los 700 caracteres.")
        self.__caption = text if text else ""

    @property
    def schedule_time(self) -> datetime:
        return self.__schedule_time

    @schedule_time.setter
    def schedule_time(self, time_obj: datetime):
        if not isinstance(time_obj, datetime):
            raise TypeError("La hora debe ser un objeto datetime válido.")
        if time_obj < datetime.now():
            raise ValueError("No puedes programar en el pasado.")
        self.__schedule_time = time_obj