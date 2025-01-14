import threading
import time
import logging
from typing import Callable, Optional
from utils import play_sound, send_notification
from config import DEFAULT_WORK_TIME, DEFAULT_SHORT_BREAK, DEFAULT_LONG_BREAK, DEFAULT_ROUNDS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PomodoroTimer:
    def __init__(self, 
                 work_time: int = DEFAULT_WORK_TIME,
                 short_break: int = DEFAULT_SHORT_BREAK,
                 long_break: int = DEFAULT_LONG_BREAK,
                 rounds: int = DEFAULT_ROUNDS,
                 on_tick: Optional[Callable[[int], None]] = None,
                 on_state_change: Optional[Callable[[str], None]] = None):
        
        self.work_time = max(1, work_time) * 60
        self.short_break = max(1, short_break) * 60
        self.long_break = max(1, long_break) * 60
        self.rounds = max(1, rounds)
        
        self.current_round = 1
        self.time_left = self.work_time
        self.is_work = True
        self.is_running = False
        self.is_paused = False
        self._error_count = 0
        self._max_errors = 3
        
        self._timer_thread = None
        self._stop_event = threading.Event()
        self._error_lock = threading.Lock()
        
        self.on_tick = on_tick
        self.on_state_change = on_state_change
        
        logger.info("PomodoroTimer инициализирован")

    def _handle_error(self, error: Exception, context: str):
        """Обработка ошибок с подсчетом их количества"""
        with self._error_lock:
            self._error_count += 1
            logger.error(f"Ошибка в {context}: {error}")
            if self._error_count >= self._max_errors:
                logger.error("Достигнут лимит ошибок, останавливаем таймер")
                self.stop()
                return False
        return True

    def start_work(self):
        """Запуск рабочего периода"""
        try:
            self._error_count = 0  # Сброс счетчика ошибок при новом запуске
            self.is_work = True
            self.time_left = self.work_time
            self._start_timer()
            if self.on_state_change:
                try:
                    self.on_state_change('work')
                except Exception as e:
                    self._handle_error(e, "start_work")
            logger.info("Начат рабочий период")
        except Exception as e:
            if not self._handle_error(e, "start_work"):
                raise

    def start_break(self):
        """Запуск перерыва"""
        try:
            self.is_work = False
            self.time_left = self.long_break if self.current_round >= self.rounds else self.short_break
            self._start_timer()
            if self.on_state_change:
                try:
                    self.on_state_change('break')
                except Exception as e:
                    self._handle_error(e, "start_break")
            logger.info(f"Начат перерыв")
        except Exception as e:
            if not self._handle_error(e, "start_break"):
                raise

    def pause(self):
        """Приостановка таймера"""
        try:
            self.is_paused = True
            if self.on_state_change:
                try:
                    self.on_state_change('pause')
                except Exception as e:
                    self._handle_error(e, "pause")
            logger.info("Таймер приостановлен")
        except Exception as e:
            if not self._handle_error(e, "pause"):
                raise

    def resume(self):
        """Возобновление таймера"""
        try:
            self.is_paused = False
            if self.on_state_change:
                try:
                    self.on_state_change('work' if self.is_work else 'break')
                except Exception as e:
                    self._handle_error(e, "resume")
            logger.info("Таймер возобновлен")
        except Exception as e:
            if not self._handle_error(e, "resume"):
                raise

    def stop(self):
        """Остановка таймера"""
        try:
            self._stop_event.set()
            if self._timer_thread and self._timer_thread.is_alive():
                try:
                    self._timer_thread.join(timeout=0.1)
                except Exception as e:
                    logger.error(f"Ошибка при остановке потока таймера: {e}")
            
            self.is_running = False
            self.is_paused = False
            if self.on_state_change:
                try:
                    self.on_state_change('stop')
                except Exception as e:
                    self._handle_error(e, "stop")
            logger.info("Таймер остановлен")
        except Exception as e:
            if not self._handle_error(e, "stop"):
                raise

    def get_time_left(self) -> int:
        """Получение оставшегося времени в секундах"""
        try:
            return max(0, self.time_left)
        except Exception as e:
            logger.error(f"Ошибка при получении оставшегося времени: {e}")
            return 0

    def next_cycle(self):
        """Переход к следующему циклу"""
        try:
            if self.is_work:
                if self.current_round >= self.rounds:
                    self.current_round = 1
                else:
                    self.current_round += 1
                self.start_break()
            else:
                self.start_work()
            logger.info(f"Переход к следующему циклу (Раунд: {self.current_round})")
        except Exception as e:
            if not self._handle_error(e, "next_cycle"):
                raise

    def _start_timer(self):
        """Запуск таймера в отдельном потоке"""
        try:
            if self.is_running:
                self.stop()
            
            self._stop_event.clear()
            self.is_running = True
            self.is_paused = False
            
            self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self._timer_thread.start()
            logger.info("Запущен новый поток таймера")
        except Exception as e:
            if not self._handle_error(e, "_start_timer"):
                raise

    def _timer_loop(self):
        """Основной цикл таймера"""
        error_count = 0
        while self.time_left > 0 and not self._stop_event.is_set():
            try:
                if not self.is_paused:
                    if self.on_tick:
                        try:
                            self.on_tick(self.time_left)
                        except Exception as e:
                            if not self._handle_error(e, "_timer_loop.on_tick"):
                                break
                    
                    time.sleep(1)
                    self.time_left -= 1
                    
                    if self.time_left <= 0:
                        try:
                            play_sound()
                            if self.is_work:
                                message = "Время работы закончилось!\nНачинается 5-минутный перерыв."
                            else:
                                next_session = "25-минутная работа"
                                message = f"Перерыв закончился!\nНачинается {next_session}."
                            send_notification("Pomodoro Timer", message)
                        except Exception as e:
                            logger.error(f"Ошибка при отправке уведомления: {e}")
                        self.next_cycle()
                        break
                else:
                    time.sleep(0.1)
            except Exception as e:
                error_count += 1
                logger.error(f"Ошибка в цикле таймера: {e}")
                if error_count >= 3:  # Если произошло 3 ошибки подряд
                    logger.error("Слишком много ошибок в цикле таймера, останавливаем")
                    self.stop()
                    break
                time.sleep(1)  # Пауза перед следующей попыткой
        
        self.is_running = False
        logger.info("Цикл таймера завершен")
