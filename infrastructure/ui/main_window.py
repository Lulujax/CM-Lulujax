import os
import pyautogui
from datetime import datetime, timedelta
from typing import List
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QFileDialog, 
    QMessageBox, QCheckBox, QComboBox, QFrame,
    QSystemTrayIcon, QMenu, QApplication, QStyle
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QSettings, QSize, QPoint

from core.entities.post import Post
from core.services.scheduler import SchedulerService
from core.ports.publisher_service import PublisherService

# --- ESTILOS CSS ---
STYLESHEET = """
QMainWindow { background-color: #1a1a2e; }
QLabel { color: #e0e0e0; font-family: 'Segoe UI'; font-size: 13px; }
QLabel#Title { color: #2979FF; font-size: 20px; font-weight: bold; }
QPushButton { background-color: #0f3460; color: white; border-radius: 5px; padding: 8px; font-size: 13px; font-weight: bold; }
QPushButton:hover { background-color: #16213e; border: 1px solid #2979FF; }
QPushButton#ActionBtn { background-color: #e94560; font-size: 15px; padding: 12px; }
QPushButton#ActionBtn:hover { background-color: #c0354e; }
QTextEdit { background-color: #16213e; color: white; border: 1px solid #0f3460; border-radius: 5px; font-family: 'Segoe UI Emoji'; font-size: 13px; }
QComboBox { background-color: #16213e; color: white; border: 1px solid #0f3460; padding: 5px; }
QCheckBox { color: white; font-size: 13px; spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QFrame#Panel { background-color: #16213e; border-radius: 10px; }
"""

class WorkerSignals(QObject):
    log = pyqtSignal(str)

class MainWindow(QMainWindow):
    def __init__(self, drivers_dependencies: List[PublisherService]):
        super().__init__()
        
        self.setWindowTitle("CM Dashboard | Lulujax Edition")
        
        # Variable para controlar el cierre real
        self.force_close = False 
        
        self.settings = QSettings("LulujaxSoft", "CMAutoPoster")
        saved_size = self.settings.value("window_size", QSize(900, 650))
        saved_pos = self.settings.value("window_pos", QPoint(100, 100))
        
        self.resize(saved_size)
        self.move(saved_pos)

        self.setStyleSheet(STYLESHEET)

        self.available_drivers = drivers_dependencies
        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.scheduler = None 
        self.selected_image_path = None
        
        self.init_ui()
        
        # --- NUEVO: INICIALIZAR BANDEJA DEL SISTEMA ---
        self.init_system_tray()

    def init_system_tray(self):
        """Configura el ícono al lado del reloj"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Usamos un ícono estándar del sistema para no complicarnos con archivos .ico
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Crear el menú de clic derecho
        tray_menu = QMenu()
        
        action_show = QAction("📲 Abrir Dashboard", self)
        action_show.triggered.connect(self.show_window)
        tray_menu.addAction(action_show)
        
        tray_menu.addSeparator()
        
        action_quit = QAction("❌ Cerrar Totalmente", self)
        action_quit.triggered.connect(self.quit_application)
        tray_menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Si le das doble clic al ícono, se abre
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

    def show_window(self):
        self.show()
        self.setWindowState(Qt.WindowState.WindowNoState)
        self.raise_()
        self.activateWindow()

    def quit_application(self):
        """Esta función SÍ cierra el programa de verdad"""
        self.force_close = True
        self.close()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def closeEvent(self, event):
        """
        MAGIA AQUÍ: Interceptamos el botón X.
        Si force_close es False, solo ocultamos.
        Si force_close es True, cerramos de verdad.
        """
        if self.force_close:
            self.settings.setValue("window_size", self.size())
            self.settings.setValue("window_pos", self.pos())
            event.accept()
        else:
            event.ignore() # Ignorar la orden de cierre
            self.hide() # Solo esconder
            self.tray_icon.showMessage(
                "CM Bot - Segundo Plano",
                "El bot sigue activo aquí. Doble clic para abrir.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10) 
        central_widget.setLayout(main_layout)

        # --- PANEL IZQUIERDO ---
        left_panel = QFrame()
        left_panel.setObjectName("Panel")
        left_layout = QVBoxLayout()
        left_layout.setSpacing(10)
        left_panel.setLayout(left_layout)
        
        lbl_title = QLabel("NUEVA CAMPAÑA")
        lbl_title.setObjectName("Title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_title)
        
        self.btn_img = QPushButton("📂 Seleccionar Creativo")
        self.btn_img.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_img.clicked.connect(self.select_image)
        left_layout.addWidget(self.btn_img)
        
        self.lbl_path = QLabel("Sin archivo seleccionado")
        self.lbl_path.setStyleSheet("color: gray; font-size: 11px;")
        self.lbl_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.lbl_path)

        lbl_hint = QLabel("💡 Recomendado: Imágenes 1080x1920 (9:16) para Historias.")
        lbl_hint.setStyleSheet("color: #FFB74D; font-size: 11px; font-style: italic;") 
        lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_hint)

        left_layout.addWidget(QLabel("📢 Publicar en:"))
        
        self.checks = [] 
        for driver in self.available_drivers:
            chk = QCheckBox(f" {driver.get_name()}")
            chk.setChecked(True)
            chk.setCursor(Qt.CursorShape.PointingHandCursor)
            chk.driver_ref = driver 
            left_layout.addWidget(chk)
            self.checks.append(chk)

        h_text_layout = QHBoxLayout()
        h_text_layout.addWidget(QLabel("Copywriting:"))
        btn_emoji = QPushButton("😊 Emojis")
        btn_emoji.setFixedSize(70, 25)
        btn_emoji.setStyleSheet("background-color: transparent; border: 1px solid #555; font-size: 11px;")
        btn_emoji.clicked.connect(self.open_emoji_panel)
        h_text_layout.addWidget(btn_emoji)
        left_layout.addLayout(h_text_layout)

        self.txt_caption = QTextEdit()
        self.txt_caption.setPlaceholderText("Describe tu publicación... 🔥")
        self.txt_caption.setFixedHeight(80)
        left_layout.addWidget(self.txt_caption)

        self.check_sched = QCheckBox("📅 Programar Envío")
        self.check_sched.toggled.connect(self.toggle_scheduler)
        left_layout.addWidget(self.check_sched)
        
        self.frame_time = QWidget()
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0,0,0,0)
        self.frame_time.setLayout(time_layout)
        
        self.combo_hh = QComboBox()
        self.combo_hh.addItems([f"{n:02d}" for n in range(24)])
        self.combo_hh.setCurrentText(datetime.now().strftime("%H"))
        self.combo_mm = QComboBox()
        self.combo_mm.addItems([f"{n:02d}" for n in range(0, 60, 5)])
        self.combo_mm.setCurrentText(datetime.now().strftime("%M"))
        
        time_layout.addWidget(QLabel("Hora:"))
        time_layout.addWidget(self.combo_hh)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.combo_mm)
        time_layout.addStretch()
        self.frame_time.setVisible(False)
        left_layout.addWidget(self.frame_time)

        left_layout.addSpacing(10)

        self.btn_action = QPushButton("🚀 PUBLICAR AHORA")
        self.btn_action.setObjectName("ActionBtn")
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.setFixedHeight(45)
        self.btn_action.clicked.connect(self.handle_execution)
        left_layout.addWidget(self.btn_action)

        left_layout.addStretch()

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0,0,0,0)
        right_panel.setLayout(right_layout)
        right_layout.addWidget(QLabel("REGISTRO DE ACTIVIDAD"))
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas; font-size: 12px;")
        right_layout.addWidget(self.txt_log)

        main_layout.addWidget(left_panel, 4)
        main_layout.addWidget(right_panel, 5)
        
        self.append_log("✅ Sistema Multi-Plataforma Listo.")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.selected_image_path = file_path
            self.lbl_path.setText(f"✅ {os.path.basename(file_path)}")
            self.lbl_path.setStyleSheet("color: #00FF00; font-size: 11px;")

    def open_emoji_panel(self):
        self.txt_caption.setFocus()
        try:
            pyautogui.hotkey('win', '.')
            self.emit_log("ℹ️ Panel emojis abierto.")
        except Exception:
            pass

    def toggle_scheduler(self):
        is_checked = self.check_sched.isChecked()
        self.frame_time.setVisible(is_checked)
        if is_checked:
            self.btn_action.setText("🕒 CONFIRMAR PROGRAMACIÓN")
            self.btn_action.setStyleSheet("background-color: #2979FF;")
        else:
            self.btn_action.setText("🚀 PUBLICAR AHORA")
            self.btn_action.setStyleSheet("background-color: #e94560;")

    def emit_log(self, message):
        self.signals.log.emit(message)

    def append_log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt_log.append(f"[{ts}] {message}")
        cursor = self.txt_log.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.txt_log.setTextCursor(cursor)

    def handle_execution(self):
        caption = self.txt_caption.toPlainText().strip()
        if not self.selected_image_path:
            QMessageBox.warning(self, "Error", "Selecciona una imagen.")
            return

        selected_drivers = []
        for chk in self.checks:
            if chk.isChecked():
                selected_drivers.append(chk.driver_ref)

        if not selected_drivers:
            QMessageBox.warning(self, "Error", "Selecciona al menos una red.")
            return

        self.scheduler = SchedulerService(selected_drivers, self.emit_log)
        
        future_buffer = datetime.now() + timedelta(minutes=2)
        try:
            post = Post(self.selected_image_path, caption, future_buffer)
        except ValueError as e:
            QMessageBox.critical(self, "Error de Validación", str(e))
            return

        self.btn_action.setEnabled(False)
        self.btn_action.setText("⚙️ PROCESANDO EN 2DO PLANO...")

        if self.check_sched.isChecked():
            hh = int(self.combo_hh.currentText())
            mm = int(self.combo_mm.currentText())
            self.scheduler.schedule_post(post, hh, mm)
            QMessageBox.information(self, "Listo", "Programado. Puedes cerrar la ventana (X) y quedaré trabajando en la barra de tareas.")
            self.btn_action.setEnabled(True)
            self.btn_action.setText("🕒 CONFIRMAR PROGRAMACIÓN")
        else:
            self.scheduler.execute_now(post)
            QThread.msleep(500)
            self.btn_action.setEnabled(True)
            self.btn_action.setText("🚀 PUBLICAR AHORA")