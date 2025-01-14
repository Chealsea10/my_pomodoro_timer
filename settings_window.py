import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                          QSpinBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtGui import QIcon
import config

class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(400, 300)
        self.settings_file = "pomodoro_settings.json"
        
        # Загружаем текущие настройки
        self.current_settings = self.load_settings()
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Время работы
        work_layout = QHBoxLayout()
        work_label = QLabel("Время работы (минуты):")
        work_label.setStyleSheet("font-weight: bold;")
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 60)
        self.work_spin.setValue(self.current_settings.get("work_time", config.DEFAULT_WORK_TIME))
        self.work_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                background: white;
                min-width: 80px;
            }
            QSpinBox:hover {
                border-color: #3498DB;
            }
        """)
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_spin)
        layout.addLayout(work_layout)

        # Время короткого перерыва
        short_break_layout = QHBoxLayout()
        short_break_label = QLabel("Короткий перерыв (минуты):")
        short_break_label.setStyleSheet("font-weight: bold;")
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 30)
        self.short_break_spin.setValue(self.current_settings.get("short_break", config.DEFAULT_SHORT_BREAK))
        self.short_break_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                background: white;
                min-width: 80px;
            }
            QSpinBox:hover {
                border-color: #3498DB;
            }
        """)
        short_break_layout.addWidget(short_break_label)
        short_break_layout.addWidget(self.short_break_spin)
        layout.addLayout(short_break_layout)

        # Время длинного перерыва
        long_break_layout = QHBoxLayout()
        long_break_label = QLabel("Длинный перерыв (минуты):")
        long_break_label.setStyleSheet("font-weight: bold;")
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 60)
        self.long_break_spin.setValue(self.current_settings.get("long_break", config.DEFAULT_LONG_BREAK))
        self.long_break_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                background: white;
                min-width: 80px;
            }
            QSpinBox:hover {
                border-color: #3498DB;
            }
        """)
        long_break_layout.addWidget(long_break_label)
        long_break_layout.addWidget(self.long_break_spin)
        layout.addLayout(long_break_layout)

        # Количество раундов
        rounds_layout = QHBoxLayout()
        rounds_label = QLabel("Раундов до длинного перерыва:")
        rounds_label.setStyleSheet("font-weight: bold;")
        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 10)
        self.rounds_spin.setValue(self.current_settings.get("rounds", config.DEFAULT_ROUNDS))
        self.rounds_spin.setStyleSheet("""
            QSpinBox {
                padding: 5px;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                background: white;
                min-width: 80px;
            }
            QSpinBox:hover {
                border-color: #3498DB;
            }
        """)
        rounds_layout.addWidget(rounds_label)
        rounds_layout.addWidget(self.rounds_spin)
        layout.addLayout(rounds_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        save_button = QPushButton("Сохранить")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #219A52;
            }
        """)
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()

        layout.addStretch()
        layout.addLayout(buttons_layout)

    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки: {str(e)}")
            return {}

    def save_settings(self):
        settings = {
            "work_time": self.work_spin.value(),
            "short_break": self.short_break_spin.value(),
            "long_break": self.long_break_spin.value(),
            "rounds": self.rounds_spin.value()
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            QMessageBox.information(self, "Успех", "Настройки сохранены успешно!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {str(e)}")