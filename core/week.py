from datetime import date, timedelta


class Week:
    def __init__(self, target_date: date = None):
        self.target_date = target_date or date.today()
        self.start_monday = self._get_start_monday()
        self.current_monday = self._get_current_monday()
        self.week_number = self._calculate_week_number()

    def _get_start_monday(self) -> date:
        """Возвращает первый понедельник учебного года"""
        # Определение года начала учебного года
        year = self.target_date.year if self.target_date.month >= 9 else self.target_date.year - 1

        # Проверка дня начала учебного года
        start_date = date(year, 9, 1)
        if start_date.weekday() == 6:  # Если воскресенье
            start_date += timedelta(days=1)

        # Возврат начала учебного года
        return start_date - timedelta(days=start_date.weekday())

    def _get_current_monday(self) -> date:
        """Возвращает понедельник текущей недели"""
        return self.target_date - timedelta(days=self.target_date.weekday())

    def _calculate_week_number(self) -> int:
        """Номер недели начиная с первой недели учебного года"""
        delta = (self.current_monday - self.start_monday).days
        return (delta // 7) + 1

    def is_upper(self) -> bool:
        """Возвращает True для верхней недели"""
        return self.week_number % 2 == 1

    def week_type(self) -> str:
        """Возвращает 'верхняя' или 'нижняя'"""
        return "верхняя" if self.is_upper() else "нижняя"

    def next_week(self):
        """Возвращает объект Week для следующей недели"""
        next_monday = self.current_monday + timedelta(days=7)
        return Week(next_monday)

    def __str__(self):
        return f"{self.week_type()} неделя (№{self.week_number}|{self.is_upper()})".capitalize()
