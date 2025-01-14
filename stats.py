import pandas as pd
from datetime import datetime
import os
from config import STATS_FILE

class PomodoroStats:
    def __init__(self):
        self.stats_file = STATS_FILE
        self._create_stats_file_if_not_exists()

    def _create_stats_file_if_not_exists(self):
        """Создание файла статистики, если он не существует"""
        if not os.path.exists(self.stats_file):
            df = pd.DataFrame(columns=['date', 'work_minutes'])
            df.to_csv(self.stats_file, index=False)

    def add_session(self, work_minutes: int):
        """
        Добавление новой сессии в статистику
        
        Args:
            work_minutes: количество отработанных минут
        """
        today = datetime.now().strftime('%Y-%m-%d')
        new_data = pd.DataFrame({'date': [today], 'work_minutes': [work_minutes]})
        
        try:
            df = pd.read_csv(self.stats_file)
            df = pd.concat([df, new_data], ignore_index=True)
            df.to_csv(self.stats_file, index=False)
        except Exception as e:
            print(f"Ошибка при сохранении статистики: {e}")

    def get_today_stats(self) -> int:
        """Получение статистики за сегодня"""
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            df = pd.read_csv(self.stats_file)
            return df[df['date'] == today]['work_minutes'].sum()
        except Exception:
            return 0

    def get_total_stats(self) -> dict:
        """Получение общей статистики"""
        try:
            df = pd.read_csv(self.stats_file)
            return {
                'total_minutes': df['work_minutes'].sum(),
                'total_sessions': len(df),
                'average_session': round(df['work_minutes'].mean(), 1)
            }
        except Exception:
            return {'total_minutes': 0, 'total_sessions': 0, 'average_session': 0}
