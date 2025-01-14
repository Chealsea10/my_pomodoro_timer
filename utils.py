from plyer import notification
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def play_sound():
    """
    Воспроизведение звукового сигнала
    В реальном приложении здесь можно использовать pygame или другую библиотеку
    """
    logger.info("🔔 Звуковой сигнал!")

def send_notification(title: str, message: str):
    """
    Отправка системного уведомления
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_icon=None,  # здесь можно указать путь к иконке
            timeout=10,
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
        logger.info(f"📢 {title}: {message}")

def format_time(seconds: int) -> str:
    """
    Форматирование времени в формат MM:SS
    """
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"
