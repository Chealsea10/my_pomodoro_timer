import sys
import os
import json
import random
import logging
import pygame
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QProgressBar, QMessageBox, QHBoxLayout,
                             QDialog)
from PyQt6.QtCore import Qt, QTimer, QUrl, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QCloseEvent, QPixmap, QIcon
import config
from pomodoro import PomodoroTimer
from utils import format_time
from stats import PomodoroStats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PomodoroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setFixedSize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Устанавливаем иконку приложения
        app_icon = QIcon(config.WORK_IMAGES[0])  # Используем work.png как иконку
        self.setWindowIcon(app_icon)
        
        # Флаг для отслеживания состояния звука
        self.sound_enabled = True
        
        try:
            self.stats = PomodoroStats()
            self.timer = PomodoroTimer(
                on_tick=self._safe_update_timer_display,
                on_state_change=self._safe_handle_state_change
            )
            
            # Инициализация pygame для звука
            pygame.mixer.init()
            self.notification_sound = pygame.mixer.Sound(config.NOTIFICATION_SOUND)
            self.timer_end_sound = pygame.mixer.Sound(config.TIMER_END_SOUND)
            
            # Таймер для обновления UI
            self.ui_timer = QTimer()
            self.ui_timer.timeout.connect(self._update_ui)
            self.ui_timer.start(100)  # Обновляем UI каждые 100 мс
            
            # Таймер для автосохранения
            self.auto_save_timer = QTimer()
            self.auto_save_timer.timeout.connect(self._safe_save_progress)
            self.auto_save_timer.start(60000)  # Сохраняем каждую минуту
            
            self.init_ui()
            # Загружаем пользовательские настройки после инициализации UI
            self.load_user_settings()
            logger.info("Приложение успешно инициализировано")
            
        except Exception as e:
            logger.error(f"Ошибка при инициализации приложения: {e}")
            QMessageBox.critical(self, "Ошибка запуска", 
                               "Не удалось запустить приложение. Проверьте логи для деталей.")
            sys.exit(1)
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 10, 20, 20)

            # Кнопка настроек (абсолютное позиционирование слева)
            self.settings_button = QPushButton(central_widget)
            self.settings_button.setFixedSize(32, 32)
            self.settings_button.setStyleSheet(config.SOUND_BUTTON_STYLE)  # Используем тот же стиль
            self.settings_button.setIcon(QIcon(config.SETTINGS_IMAGE))
            self.settings_button.setIconSize(QSize(28, 28))
            self.settings_button.clicked.connect(self.show_settings)
            self.settings_button.move(20, 10)  # 20px отступ слева

            # Кнопка звука (абсолютное позиционирование справа)
            self.sound_button = QPushButton(central_widget)
            self.sound_button.setFixedSize(32, 32)
            self.sound_button.setStyleSheet(config.SOUND_BUTTON_STYLE)
            self.sound_button.clicked.connect(self.toggle_sound)
            self._update_sound_button_icon()
            self.sound_button.move(self.width() - 52, 10)  # 20px отступ справа + 32px ширина

            # Изображение
            self.image_label = QLabel()
            self.image_label.setFixedSize(280, 220)
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._set_image(config.STOP_IMAGE)
            layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignHCenter)

            # Таймер
            initial_time = self.timer.work_time if hasattr(self, 'timer') else config.DEFAULT_WORK_TIME * 60
            self.time_label = QLabel(format_time(initial_time))
            self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.time_label.setStyleSheet("""
                QLabel {
                    font-size: 72px;
                    font-weight: bold;
                    color: #2C3E50;
                    padding: 10px 0;
                }
            """)
            layout.addWidget(self.time_label)

            # Прогресс бар
            progress_widget = QWidget()
            progress_layout = QHBoxLayout(progress_widget)  # Используем горизонтальный layout
            progress_layout.setContentsMargins(20, 5, 20, 5)  # Отступы слева и справа
            
            self.progress_bar = QProgressBar()
            self.progress_bar.setFixedHeight(16)
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(config.DEFAULT_WORK_TIME * 60)
            self.progress_bar.setValue(0)
            self.progress_bar.setStyleSheet(config.PROGRESS_BAR_PAUSE_STYLE)
            self.progress_bar.setTextVisible(True)
            self.progress_bar.setFormat("%p%")
            progress_layout.addWidget(self.progress_bar)
            
            layout.addWidget(progress_widget)

            # Кнопки
            buttons_widget = QWidget()
            buttons_layout = QVBoxLayout(buttons_widget)
            buttons_layout.setSpacing(5)  # Расстояние между кнопками 30px
            buttons_layout.setContentsMargins(0, 0, 0, 10)  # Уменьшаем верхний отступ до 10px

            # Кнопка Старт/Продолжить
            self.start_button = QPushButton("Начать")
            self.start_button.clicked.connect(self.toggle_timer)
            self.start_button.setStyleSheet(config.BUTTON_STYLE)
            buttons_layout.addWidget(self.start_button)

            # Кнопка Статистика
            self.stats_button = QPushButton("Статистика")
            self.stats_button.clicked.connect(self.show_stats)
            self.stats_button.setStyleSheet(config.BUTTON_STYLE)
            buttons_layout.addWidget(self.stats_button)

            # Кнопка Стоп
            self.stop_button = QPushButton("Стоп")
            self.stop_button.clicked.connect(self.stop_timer)
            self.stop_button.setEnabled(False)
            self.stop_button.setStyleSheet(config.BUTTON_STYLE)
            buttons_layout.addWidget(self.stop_button)

            layout.addWidget(buttons_widget)

            # Статус и статистика
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setSpacing(5)
            info_layout.setContentsMargins(0, 0, 0, 0)

            self.status_label = QLabel("Готов к работе")
            self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.status_label.setStyleSheet(config.LABEL_STYLE)
            info_layout.addWidget(self.status_label)

            self.stats_label = QLabel()
            self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stats_label.setStyleSheet(config.LABEL_STYLE)
            self.update_stats_display()
            info_layout.addWidget(self.stats_label)

            layout.addWidget(info_widget)

            # Обработчик изменения размера окна для кнопки звука
            self.resizeEvent = self.on_resize

        except Exception as e:
            logger.error(f"Ошибка при инициализации UI: {e}")
            raise

    def on_resize(self, event):
        """Обработчик изменения размера окна"""
        try:
            # Обновляем позиции кнопок
            self.settings_button.move(20, 10)  # Левый угол
            self.sound_button.move(self.width() - 52, 10)  # Правый угол
            super().resizeEvent(event)
        except Exception as e:
            logger.error(f"Ошибка при обработке изменения размера окна: {e}")

    def load_user_settings(self):
        """Загрузка пользовательских настроек"""
        try:
            settings_file = "pomodoro_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.timer.work_time = settings.get("work_time", config.DEFAULT_WORK_TIME) * 60
                    self.timer.short_break = settings.get("short_break", config.DEFAULT_SHORT_BREAK) * 60
                    self.timer.long_break = settings.get("long_break", config.DEFAULT_LONG_BREAK) * 60
                    self.timer.rounds = settings.get("rounds", config.DEFAULT_ROUNDS)
                    # Обновляем максимальное значение прогресс-бара и время
                    initial_time = settings.get("work_time", config.DEFAULT_WORK_TIME) * 60
                    self.progress_bar.setMaximum(initial_time)
                    self.progress_bar.setValue(0)  # Сбрасываем прогресс
                    self.time_label.setText(format_time(initial_time))
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек: {e}")

    def show_settings(self):
        """Показать окно настроек"""
        try:
            from settings_window import SettingsWindow
            settings_window = SettingsWindow(self)
            if settings_window.exec() == QDialog.DialogCode.Accepted:
                # Перезагружаем настройки
                self.load_user_settings()
                # Если таймер остановлен, обновляем отображение
                if not self.timer.is_running:
                    self.stop_timer()
        except Exception as e:
            logger.error(f"Ошибка при отображении окна настроек: {e}")

    def _set_image(self, image_path: str):
        """Установка изображения"""
        try:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(280, 220,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
            logger.error(f"Ошибка при установке изображения: {e}")

    def _safe_update_timer_display(self, time_left: int):
        """Безопасное обновление отображения таймера"""
        try:
            self.time_label.setText(format_time(time_left))
            self.progress_bar.setValue(time_left)
        except Exception as e:
            logger.error(f"Ошибка при обновлении дисплея: {e}")

    def _play_notification(self):
        """Воспроизведение звука уведомления"""
        try:
            if self.sound_enabled:
                self.notification_sound.play()
        except Exception as e:
            logger.error(f"Ошибка при воспроизведении звука: {e}")

    def _safe_handle_state_change(self, state: str):
        """Безопасная обработка изменения состояния"""
        try:
            # Воспроизводим звук при смене состояния
            if self.sound_enabled:
                if state in ['break', 'long_break']:
                    self.timer_end_sound.play()
                else:
                    self.notification_sound.play()
            
            if state == 'work':
                self.status_label.setText("Время работать!")
                self.progress_bar.setMaximum(self.timer.work_time)
                self._set_color_theme('work')
                self._set_image(random.choice(config.WORK_IMAGES))
            elif state == 'break':
                self.status_label.setText("Время отдыхать!")
                self.progress_bar.setMaximum(self.timer.short_break)
                self._set_color_theme('break')
                self._set_image(random.choice(config.PAUSE_IMAGES))
            elif state == 'long_break':
                self.status_label.setText("Большой перерыв!")
                self.progress_bar.setMaximum(self.timer.long_break)
                self._set_color_theme('long_break')
                self._set_image(random.choice(config.PAUSE_IMAGES))
            elif state == 'pause':
                self.status_label.setText("Пауза")
                self._set_color_theme('pause')
            elif state == 'stop':
                self.status_label.setText("Готов к работе")
                self.start_button.setText("Начать")
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self._set_color_theme('pause')
                self._set_image(config.STOP_IMAGE)
                self.update_stats_display()
            
            self.update_stats_display()
        except Exception as e:
            logger.error(f"Ошибка при обработке изменения состояния: {e}")

    def _set_color_theme(self, state: str):
        """Установка цветовой темы"""
        try:
            if state == 'work':
                self.progress_bar.setStyleSheet(config.PROGRESS_BAR_WORK_STYLE)
            elif state in ['break', 'long_break']:
                self.progress_bar.setStyleSheet(config.PROGRESS_BAR_BREAK_STYLE)
            else:  # pause or stop
                self.progress_bar.setStyleSheet(config.PROGRESS_BAR_PAUSE_STYLE)
        except Exception as e:
            logger.error(f"Ошибка при установке цветовой темы: {e}")

    def _update_ui(self):
        """Обновление UI"""
        try:
            if self.timer.is_running and not self.timer.is_paused:
                # Обновляем время
                self.time_label.setText(format_time(self.timer.time_left))
                # Обновляем прогресс-бар
                self.progress_bar.setValue(self.timer.time_left)
        except Exception as e:
            logger.error(f"Ошибка при обновлении UI: {e}")

    def _safe_save_progress(self):
        """Безопасное сохранение прогресса"""
        try:
            if self.timer.is_work and not self.timer.is_paused and self.timer.is_running:
                # Сохраняем только одну минуту за каждый вызов
                self.stats.add_session(1)
                self.update_stats_display()
        except Exception as e:
            logger.error(f"Ошибка при сохранении прогресса: {e}")

    def toggle_timer(self):
        """Переключение состояния таймера"""
        try:
            if self.start_button.text() == "Начать":
                # Запускаем таймер
                self.timer.start_work()
                self.start_button.setText("Пауза")
                self.start_button.setEnabled(True)  # Кнопка паузы активна
                self.stop_button.setEnabled(True)
            elif self.start_button.text() == "Пауза":
                # Ставим на паузу
                self.timer.pause()
                self.start_button.setText("Продолжить")
            else:  # текст кнопки "Продолжить"
                # Возобновляем таймер
                self.timer.resume()
                self.start_button.setText("Пауза")
        except Exception as e:
            logger.error(f"Ошибка при переключении таймера: {e}")

    def start_timer(self):
        """Запуск таймера"""
        try:
            self.timer.start()
            self.start_button.setText("Пауза")
            self.stop_button.setEnabled(True)
        except Exception as e:
            logger.error(f"Ошибка при запуске таймера: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось запустить таймер")

    def stop_timer(self):
        """Остановка таймера"""
        try:
            self.timer.stop()
            # Сбрасываем UI, используя текущее значение времени работы
            initial_time = self.timer.work_time  # Используем установленное время работы
            self.time_label.setText(format_time(initial_time))
            self.progress_bar.setMaximum(initial_time)
            self.progress_bar.setValue(0)
            # Обновляем кнопки
            self.start_button.setText("Начать")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self._set_image(config.STOP_IMAGE)
            self.status_label.setText("Готов к работе")
            self.update_stats_display()
        except Exception as e:
            logger.error(f"Ошибка при остановке таймера: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось остановить таймер")

    def show_stats(self):
        """Показать окно статистики"""
        try:
            from stats_window import StatsWindow
            stats_window = StatsWindow(config.STATS_FILE)
            stats_window.exec()
        except Exception as e:
            logger.error(f"Ошибка при отображении статистики: {e}")
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть статистику")

    def update_stats_display(self):
        """Обновление отображения статистики"""
        try:
            today_minutes = self.stats.get_today_stats()
            total_stats = self.stats.get_total_stats()
            
            self.stats_label.setText(
                f"Сегодня: {today_minutes} мин\n"
                f"Всего: {today_minutes} мин ({total_stats['total_sessions']} сессий)"
            )
        except Exception as e:
            logger.error(f"Ошибка при обновлении статистики: {e}")

    def toggle_sound(self):
        """Включение/выключение звука"""
        try:
            self.sound_enabled = not self.sound_enabled
            self._update_sound_button_icon()
        except Exception as e:
            logger.error(f"Ошибка при переключении звука: {e}")
            
    def _update_sound_button_icon(self):
        """Обновление иконки кнопки звука"""
        try:
            icon = QIcon(config.SOUND_ON_IMAGE if self.sound_enabled else config.SOUND_OFF_IMAGE)
            self.sound_button.setIcon(icon)
            self.sound_button.setIconSize(QSize(28, 28))
        except Exception as e:
            logger.error(f"Ошибка при обновлении иконки звука: {e}")

    def closeEvent(self, event: QCloseEvent):
        """Обработка закрытия приложения"""
        try:
            pygame.mixer.quit()  # Закрываем pygame mixer при выходе
            self._safe_save_progress()  # Сохраняем прогресс перед закрытием
            if self.timer.is_running:
                self.stop_timer()
            event.accept()
        except Exception as e:
            logger.error(f"Ошибка при закрытии приложения: {e}")
            event.accept()  # Принимаем событие закрытия даже при ошибке

def main():
    try:
        app = QApplication(sys.argv)
        
        # Устанавливаем иконку для всего приложения
        app_icon = QIcon(config.WORK_IMAGES[0])
        app.setWindowIcon(app_icon)
        
        window = PomodoroApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Критическая ошибка приложения: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
