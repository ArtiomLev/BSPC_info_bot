import locale
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any

# Установка локали
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Для Unix/Linux
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')  # Для Windows


class ReplacementSchedule:
    def __init__(self, base_url: str, base_link: str):
        self.url = base_url  # Адрес сайта
        self.base_link = base_link  # Ссылка на страницу со ссылками на замены
        self.replacements_links = {}  # Найденные ссылки на замены

    def fetch_replacements_links(self):
        url = self.url + self.base_link
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table', class_='category')
        if not table:
            return

        rows = table.find_all('tr')
        for row in rows:
            link_tag = row.find('a')
            if link_tag:
                day_name = link_tag.text.strip()
                link = link_tag['href']
                full_link = f"{self.url}{link}"
                self.replacements_links[day_name] = full_link

    def get_replacements_raw(self, day_name=None):
        if not self.replacements_links:
            self.fetch_replacements_links()

        if day_name:
            day_name = day_name.capitalize()
            if day_name not in self.replacements_links:
                return None
            url = self.replacements_links[day_name]
        else:
            today = datetime.now().strftime('%A')
            day_name = today.capitalize()
            if day_name not in self.replacements_links:
                return None
            url = self.replacements_links[day_name]

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        replacements_dict = {}
        content_div = soup.find('div', id='MCZ_Content')
        if not content_div:
            return None

        tables = content_div.find_all('table', border="1")
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue

            group_name_idx = 0
            pair_number_idx = 1
            old_subject_idx = 2
            new_subject_idx = 3
            teacher_idx = 4
            cabinet_idx = 5

            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) != 6:
                    continue

                try:
                    group_name = cells[group_name_idx].text.strip() if group_name_idx is not None else "-"
                    pair_number = cells[pair_number_idx].text.strip() if pair_number_idx is not None else '-'
                    old_subject = cells[old_subject_idx].text.strip() if old_subject_idx is not None else '-'
                    new_subject = cells[new_subject_idx].text.strip() if new_subject_idx is not None else '-'
                    teacher = cells[teacher_idx].text.strip() if teacher_idx is not None else '-'
                    cabinet = cells[cabinet_idx].text.strip() if cabinet_idx is not None else '-'
                except IndexError:
                    continue

                if (group_name == ""
                        and pair_number == ""
                        and old_subject == ""
                        and new_subject == ""
                        and teacher == ""
                        and cabinet == ""):
                    continue

                if group_name not in replacements_dict:
                    replacements_dict[group_name] = []

                if new_subject == "-" and teacher == "-" and cabinet == "-":
                    replacements_dict[group_name] += [[
                        "pair_remove",
                        {
                            "pair_number": pair_number,
                            "subject": old_subject,
                        }
                    ]]
                elif old_subject == "-":
                    replacements_dict[group_name] += [[
                        "pair_add",
                        {
                            "pair_number": pair_number,
                            "subject": new_subject,
                            "teacher": teacher,
                            "cabinet": cabinet
                        }
                    ]]
                elif new_subject == "→" and cabinet == "":
                    replacements_dict[group_name] += [[
                        "cabinet_change",
                        {
                            "pair_number": pair_number,
                            "old_cabinet": old_subject,
                            "new_cabinet": teacher
                        }
                    ]]
                else:
                    replacements_dict[group_name] += [[
                        "pair_change",
                        {
                            "pair_number": pair_number,
                            "old_subject": old_subject,
                            "new_subject": new_subject,
                            "teacher": teacher,
                            "cabinet": cabinet
                        }
                    ]]

        return replacements_dict if replacements_dict else None

    def get_replacements(self, day_name=None):
        replacements = self.get_replacements_raw(day_name)
        return Replacements(replacements) if replacements is not None else f"Замены для {day_name} не найдены."


class Replacements:
    def __init__(self, data: Dict[str, List[List[Any]]]):
        """
        Принимает на вход словарь с заменами в формате:
        {
            group_name: [
                [type, {pair_number: str, ...}],
                ...
            ],
            ...
        }
        Сортирует замены в каждой группе по возрастанию номера пары.
        Если значение pair_number представляет собой более одной цифры (например, время "13:35-14:20"),
        то такие записи помещаются в конец.
        """
        self._data: Dict[str, List[List[Any]]] = {}
        for group, entries in data.items():
            # Сортировка: single-digit numbers first, then все прочие (включая времена) в конец
            def sort_key(e: List[Any]) -> float:
                pn = e[1].get('pair_number', '')
                # Если строка ровно из одной цифры
                if isinstance(pn, str) and len(pn) == 1 and pn.isdigit():
                    return int(pn)
                # Во всех других случаях (время или многозначные числа) ставим в конец
                return float('inf')

            sorted_entries = sorted(entries, key=sort_key)
            self._data[group] = sorted_entries

    def get_all(self) -> Dict[str, List[List[Any]]]:
        """Возвращает все замены в исходном (отсортированном) формате."""
        return self._data

    def has_group(self, group: str) -> bool:
        """Проверяет, есть ли замены для заданной группы."""
        return group in self._data

    def get_groups(self) -> List[str]:
        """Возвращает список всех групп, для которых есть замены."""
        return list(self._data.keys())

    def get_group_replacements(self, group: str) -> List[List[Any]]:
        """Возвращает список замен для заданной группы."""
        return self._data.get(group, [])

    def has_teacher(self, last_name: str) -> bool:
        """Проверяет, есть ли замены, связанные с преподавателем (по фамилии)."""
        for entries in self._data.values():
            for entry in entries:
                _, info = entry
                teacher_field = info.get('teacher')
                if teacher_field:
                    for name in teacher_field.split('/'):
                        if name.strip() == last_name:
                            return True
        return False

    def get_teacher_replacements(self, last_name: str) -> List[List[Any]]:
        """
        Возвращает все замены для преподавателя по фамилии.
        Каждый элемент: [group, type, pair_number, ...other fields без 'teacher']
        Отсортировано: сначала single-digit номера, затем все прочие (время и др.).
        """
        matches: List[List[Any]] = []
        for group, entries in self._data.items():
            for entry in entries:
                entry_type, info = entry
                teacher_field = info.get('teacher')
                if not teacher_field:
                    continue
                names = [n.strip() for n in teacher_field.split('/')]
                if last_name in names:
                    base = [group, entry_type, info.get('pair_number', '')]
                    for key, value in info.items():
                        if key in ('teacher', 'pair_number'):
                            continue
                        base.append(value)
                    matches.append(base)

        # сортировка с учётом условия: single-digit first, остальное в конец
        def sort_key_teacher(e: List[Any]) -> float:
            pn = e[2]
            if isinstance(pn, str) and len(pn) == 1 and pn.isdigit():
                return int(pn)
            return float('inf')

        matches.sort(key=sort_key_teacher)
        return matches
