from abc import ABC, abstractmethod
import requests
from typing import List, Dict, Any


class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервисов с вакансиями"""

    @abstractmethod
    def connect(self) -> bool:
        """Подключение к API"""
        pass

    @abstractmethod
    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получение вакансий по поисковому запросу"""
        pass

    @abstractmethod
    def format_vacancy_data(self, raw_vacancy: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование данных о вакансии в единый формат"""
        pass


class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        self.base_url = "https://api.hh.ru"
        self.connected = False
        self.session = requests.Session()

    def connect(self) -> bool:
        """Подключение к API HeadHunter"""
        try:
            response = self.session.get(f"{self.base_url}/vacancies",
                                        params={"text": "test", "per_page": 1})
            if response.status_code == 200:
                self.connected = True
                return True
            return False
        except requests.exceptions.RequestException:
            return False

    def get_vacancies(self, search_query: str, **kwargs) -> List[Dict[str, Any]]:
        """Получение вакансий по поисковому запросу"""
        if not self.connected:
            if not self.connect():
                return []

        params = {
            "text": search_query,
            "area": kwargs.get('area', 1),
            "per_page": kwargs.get('per_page', 100),
            "page": kwargs.get('page', 0),
            "only_with_salary": kwargs.get('only_with_salary', False)
        }

        try:
            response = self.session.get(f"{self.base_url}/vacancies", params=params)
            response.raise_for_status()

            data = response.json()
            vacancies = data.get('items', [])

            formatted_vacancies = [self.format_vacancy_data(vacancy) for vacancy in vacancies]
            return formatted_vacancies

        except (requests.exceptions.RequestException, KeyError):
            return []

    def format_vacancy_data(self, raw_vacancy: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование данных о вакансии"""
        salary = raw_vacancy.get('salary')
        salary_from = salary.get('from') if salary else None
        salary_to = salary.get('to') if salary else None

        # Валидация зарплаты
        if salary_from is None and salary_to is None:
            salary_from = salary_to = 0
        elif salary_from is None:
            salary_from = salary_to
        elif salary_to is None:
            salary_to = salary_from

        snippet = raw_vacancy.get('snippet', {})
        requirement = snippet.get('requirement', '')

        return {
            'id': raw_vacancy.get('id'),
            'name': raw_vacancy.get('name'),
            'url': raw_vacancy.get('alternate_url'),
            'salary_from': salary_from,
            'salary_to': salary_to,
            'salary_currency': salary.get('currency') if salary else 'RUR',
            'employer': raw_vacancy.get('employer', {}).get('name'),
            'requirement': requirement,
            'experience': raw_vacancy.get('experience', {}).get('name'),
            'published_at': raw_vacancy.get('published_at')
        }


class Vacancy:
    """Класс для представления вакансии с валидацией данных"""

    def __init__(self, name: str, url: str, salary_from: int = None,
                 salary_to: int = None, employer: str = "", requirement: str = ""):
        self._validate_data(name, url, salary_from, salary_to)

        self.name = name
        self.url = url
        self.salary_from = salary_from or 0
        self.salary_to = salary_to or 0
        self.employer = employer
        self.requirement = requirement

        # Средняя зарплата для сравнения
        self._average_salary = (
                                           self.salary_from + self.salary_to) / 2 if self.salary_from and self.salary_to else self.salary_from or self.salary_to or 0

    def _validate_data(self, name: str, url: str, salary_from: int, salary_to: int):
        """Валидация входных данных"""
        if not name or not isinstance(name, str):
            raise ValueError("Название вакансии должно быть непустой строкой")
        if not url or not isinstance(url, str):
            raise ValueError("URL вакансии должен быть непустой строкой")
        if salary_from is not None and salary_from < 0:
            raise ValueError("Зарплата не может быть отрицательной")
        if salary_to is not None and salary_to < 0:
            raise ValueError("Зарплата не может быть отрицательной")
        if salary_from and salary_to and salary_from > salary_to:
            raise ValueError("Минимальная зарплата не может быть больше максимальной")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vacancy':
        """Создание вакансии из словаря"""
        return cls(
            name=data.get('name', ''),
            url=data.get('url', ''),
            salary_from=data.get('salary_from'),
            salary_to=data.get('salary_to'),
            employer=data.get('employer', ''),
            requirement=data.get('requirement', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование вакансии в словарь"""
        return {
            'name': self.name,
            'url': self.url,
            'salary_from': self.salary_from,
            'salary_to': self.salary_to,
            'employer': self.employer,
            'requirement': self.requirement
        }

    def __str__(self):
        salary_info = "не указана"
        if self.salary_from or self.salary_to:
            salary_info = f"{self.salary_from or '?'} - {self.salary_to or '?'}"
        return f"{self.name} | {self.employer} | Зарплата: {salary_info} | {self.url}"

    def __repr__(self):
        return f"Vacancy('{self.name}', '{self.url}', {self.salary_from}, {self.salary_to})"

    # Методы сравнения по зарплате
    def __eq__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._average_salary == other._average_salary

    def __lt__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._average_salary < other._average_salary

    def __le__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._average_salary <= other._average_salary

    def __gt__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._average_salary > other._average_salary

    def __ge__(self, other):
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._average_salary >= other._average_salary

    def has_keyword_in_requirement(self, keyword: str) -> bool:
        """Проверка наличия ключевого слова в требованиях"""
        return keyword.lower() in self.requirement.lower()


