import os

# Definimos la estructura basada en Clean Architecture
folders = [
    "core/entities",           # Reglas de negocio (Clases Post, Config)
    "core/ports",              # Interfaces (Contratos)
    "infrastructure/persistence", # Guardado de datos (JSON)
    "infrastructure/whatsapp",    # Selenium y Drivers
    "infrastructure/ui/components", # Interfaz Gráfica
    "app",                     # Main y orquestadores
    "assets",                  # Imagenes y logs
    "data"                     # Donde se guardará el JSON de la app
]

# Archivos base obligatorios para que sea un paquete Python
files = [
    "core/__init__.py",
    "core/entities/__init__.py",
    "core/ports/__init__.py",
    "infrastructure/__init__.py",
    "infrastructure/persistence/__init__.py",
    "infrastructure/whatsapp/__init__.py",
    "infrastructure/ui/__init__.py",
    "app/__init__.py",
    "app/main.py",           # Punto de entrada
    ".gitignore",            # Seguridad
    "README.md",
    "requirements.txt"       # Lista de frameworks
]

def create_structure():
    print("🚧 Creando esqueleto del proyecto CM-Lulujax...")
    
    # 1. Crear carpetas
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"  [Carpeta] {folder} creada.")

    # 2. Crear archivos vacíos
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                pass
            print(f"  [Archivo] {file} creado.")
    
    # 3. Contenido base del .gitignore (Seguridad)
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*.log

# Entorno y Secretos
.env
venv/
env/

# Datos locales (No subir al repo la base de datos de pruebas)
data/
whatsapp_session/
"""
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("  [Config] .gitignore configurado.")

    print("\n✅ ¡Esqueleto listo! Ahora puedes borrar este script.")

if __name__ == "__main__":
    create_structure()