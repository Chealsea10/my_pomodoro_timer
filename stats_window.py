import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                          QWidget, QScrollArea, QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import pandas as pd
import config

class ContributionSquare(QFrame):
    def __init__(self, color: str, tooltip: str):
        super().__init__()
        self.setFixedSize(20, 20)  # Увеличим размер квадратиков
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #ddd;")
        self.setToolTip(tooltip)

class StatsWindow(QDialog):
    def __init__(self, stats_file: str):
        super().__init__()
        self.stats_file = stats_file
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Статистика Помодоро")
        self.setFixedSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Ваша активность за последний месяц")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Создаем виджет с сеткой
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(5)  # Отступы между квадратиками
        
        # Загружаем данные
        try:
            df = pd.read_csv(self.stats_file)
            df['date'] = pd.to_datetime(df['date'])
            
            # Переименовываем колонку, если нужно
            if 'work_minutes' in df.columns:
                df = df.rename(columns={'work_minutes': 'minutes'})
            
            # Группируем данные по дате и суммируем минуты
            df = df.groupby('date')['minutes'].sum().reset_index()
            
            # Получаем последние 30 дней
            end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_date = end_date - timedelta(days=29)
            
            # Добавляем метки дней недели
            days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            for i, day in enumerate(days):
                label = QLabel(day)
                label.setStyleSheet("color: #666;")
                grid_layout.addWidget(label, i, 0)
            
            # Создаем календарь активности
            date_range = pd.date_range(start=start_date, end=end_date)
            activity_data = {date: 0 for date in date_range}
            total_minutes = 0
            active_days = 0
            
            # Заполняем данными
            for _, row in df.iterrows():
                date = row['date'].replace(hour=0, minute=0, second=0, microsecond=0)
                if date in activity_data:
                    minutes = row['minutes']
                    activity_data[date] = minutes
                    total_minutes += minutes
                    if minutes > 0:
                        active_days += 1
            
            # Заполняем сетку
            current_col = 1
            for date in date_range:
                minutes = activity_data[date]
                color = self._get_color_for_minutes(minutes)
                tooltip = f"{date.strftime('%d.%m.%Y')}\n{minutes} минут"
                square = ContributionSquare(color, tooltip)
                # Размещаем квадратик в нужной позиции (день недели, номер столбца)
                grid_layout.addWidget(square, date.weekday(), current_col)
                
                if date.weekday() == 6:  # Воскресенье
                    current_col += 1
            
            layout.addWidget(container)
            
            # Добавляем статистику
            stats_layout = QHBoxLayout()
            
            # Всего минут
            total_label = QLabel(f"Всего минут: {total_minutes}")
            total_label.setStyleSheet("font-weight: bold; margin: 10px;")
            stats_layout.addWidget(total_label)
            
            # Активных дней
            active_label = QLabel(f"Активных дней: {active_days}")
            active_label.setStyleSheet("font-weight: bold; margin: 10px;")
            stats_layout.addWidget(active_label)
            
            # Среднее в день
            avg_minutes = round(total_minutes / max(active_days, 1))
            avg_label = QLabel(f"Среднее в день: {avg_minutes} мин")
            avg_label.setStyleSheet("font-weight: bold; margin: 10px;")
            stats_layout.addWidget(avg_label)
            
            layout.addLayout(stats_layout)
            
        except Exception as e:
            error_label = QLabel(f"Ошибка при загрузке статистики: {str(e)}")
            layout.addWidget(error_label)
        
        # Легенда
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Меньше"))
        for minutes in [0, 30, 60, 90, 120]:
            square = ContributionSquare(self._get_color_for_minutes(minutes), 
                                      f"{minutes} минут")
            legend_layout.addWidget(square)
        legend_layout.addWidget(QLabel("Больше"))
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
    
    def _get_color_for_minutes(self, minutes: int) -> str:
        """Получение цвета в зависимости от количества минут"""
        if minutes == 0:
            return "#ebedf0"  # Серый
        elif minutes < 30:
            return "#9be9a8"  # Светло-зеленый
        elif minutes < 60:
            return "#40c463"  # Зеленый
        elif minutes < 90:
            return "#30a14e"  # Темно-зеленый
        else:
            return "#216e39"  # Очень темный зеленый
