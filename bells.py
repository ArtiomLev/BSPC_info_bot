from typing import Dict, List, Optional


class BellSchedule:
    """Класс для упрощения работы со списком звонков"""

    def __init__(self, bells_data: Dict[str, List]):
        self.bells = bells_data

    def get_day_bells(self, day_type: str) -> Optional[List]:
        """Получить расписание по дню"""
        return self.bells.get(day_type)

    def format_day_bells(self, day_type: str) -> str:
        """Получить отформатированное текстом расписание"""
        day_bells = self.get_day_bells(day_type)
        if day_bells is None:
            formatted_day_type = day_type.replace('_', ' ')
            return f"Расписание для *{formatted_day_type}* не найдено"

        message_header = "*Расписание звонков\n(" + day_bells[0] + ")*\n"

        i = 1
        message = ""
        for pare in day_bells[1:]:
            message += "• Пара " + i.__str__() + ":\n"
            i = i + 1
            for lesson in pare:
                message += lesson[0] + "-" + lesson[1] + "\n"

        if not message:
            formatted_day_type = day_type.replace('_', ' ')
            return f"Расписание для *{formatted_day_type}* пусто"

        return message_header + message
