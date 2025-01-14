import os

# Размеры окна
WINDOW_TITLE = "Pomodoro Timer"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 650  # Увеличиваем высоту окна

# Цвета
WORK_COLOR = "#FF6B6B"  # Красный
BREAK_COLOR = "#4ECDC4"  # Бирюзовый
PAUSE_COLOR = "#95A5A6"  # Серый

# Время (в минутах)
DEFAULT_WORK_TIME = 25
DEFAULT_SHORT_BREAK = 5
DEFAULT_LONG_BREAK = 15
DEFAULT_ROUNDS = 4

# Пути к файлам
STATS_FILE = "pomodoro_stats.csv"

# Пути к звуковым файлам
SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")
NOTIFICATION_SOUND = os.path.join(SOUNDS_DIR, "notification.mp3")
TIMER_END_SOUND = os.path.join(SOUNDS_DIR, "relax.mp3")

# Пути к изображениям
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "picture")
SOUND_ON_IMAGE = os.path.join(IMAGES_DIR, "sound_on.png")
SOUND_OFF_IMAGE = os.path.join(IMAGES_DIR, "sound_off.png")
SETTINGS_IMAGE = os.path.join(IMAGES_DIR, "settings.png")
WORK_IMAGES = [
    os.path.join(IMAGES_DIR, "work.png"),
    os.path.join(IMAGES_DIR, "work1.png")
]
PAUSE_IMAGES = [
    os.path.join(IMAGES_DIR, "pause.png"),
    os.path.join(IMAGES_DIR, "pause2.png")
]
STOP_IMAGE = os.path.join(IMAGES_DIR, "stop.png")

# Стили
SOUND_BUTTON_STYLE = """
QPushButton {
    background-color: transparent;
    border: none;
    width: 32px;
    height: 32px;
    padding: 0px;
    margin: 5px;
}
QPushButton:hover {
    background-color: rgba(52, 73, 94, 0.1);
    border-radius: 6px;
}
"""

BUTTON_STYLE = """
QPushButton {
    background-color: #34495E;
    color: #ECF0F1;
    border: none;
    border-radius: 10px;
    padding: 8px 15px;
    font-size: 14px;
    font-weight: bold;
    min-width: 100px;
    min-height: 40px;
    margin: 5px;
    text-transform: uppercase;
}

QPushButton:hover {
    background-color: #2C3E50;
}

QPushButton:pressed {
    background-color: #2C3E50;
}

QPushButton:disabled {
    background-color: #95A5A6;
}
"""

# Стили прогресс-бара для разных состояний
PROGRESS_BAR_BASE_STYLE = """
QProgressBar {
    border: 1px solid #919B9C;
    border-radius: 2px;
    background-color: #FFFFFF;
    text-align: center;
    height: 20px;
    min-width: 300px;
    font-size: 12px;
    font-weight: bold;
    color: #000000;
    margin: 0px;
    padding: 0px;
}
"""

PROGRESS_BAR_WORK_STYLE = PROGRESS_BAR_BASE_STYLE + """
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                              stop:0 #FF9B9B,
                              stop:0.5 #FF6B6B,
                              stop:1 #FF4B4B);
    border: 1px solid #CC5555;
    border-radius: 0px;
    margin: 0px;
    width: 10px;
}
"""

PROGRESS_BAR_BREAK_STYLE = PROGRESS_BAR_BASE_STYLE + """
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                              stop:0 #7EDCD4,
                              stop:0.5 #4ECDC4,
                              stop:1 #2EBDB4);
    border: 1px solid #3AA99F;
    border-radius: 0px;
    margin: 0px;
    width: 10px;
}
"""

PROGRESS_BAR_PAUSE_STYLE = PROGRESS_BAR_BASE_STYLE + """
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                              stop:0 #B5B5B6,
                              stop:0.5 #95A5A6,
                              stop:1 #758586);
    border: 1px solid #6A7677;
    border-radius: 0px;
    margin: 0px;
    width: 10px;
}
"""

LABEL_STYLE = """
QLabel {
    color: #2C3E50;
    font-weight: bold;
}
"""

MAIN_WINDOW_STYLE = """
* {
    background-color: #FDFAF6;
}
QMainWindow {
    background-color: #FDFAF6;
}
QWidget {
    background-color: #FDFAF6;
}
"""
