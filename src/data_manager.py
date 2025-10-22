import json

from src.api_requests import *


class DataManager(ABC):
    """Абстрактный класс для управления данными о вакансиях"""

    @abstractmethod
    def add_vacancy(self, vacancy: Dict[str, Any]) -> None:
        """Добавление вакансии"""
        pass

    @abstractmethod
    def get_vacancies(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Получение вакансий по критериям"""
        pass

    @abstractmethod
    def delete_vacancy(self, criteria: Dict[str, Any]) -> None:
        """Удаление вакансий по критериям"""
        pass

    # Методы для будущей интеграции с БД
    def update_vacancy(self, criteria: Dict[str, Any], update_data: Dict[str, Any]) -> None:
        """Обновление вакансий (заглушка для будущей БД)"""
        raise NotImplementedError("Метод будет реализован для работы с БД")

    def get_vacancy_count(self) -> int:
        """Получение количества вакансий (заглушка для будущей БД)"""
        raise NotImplementedError("Метод будет реализован для работы с БД")


import os


class JSONDataManager(DataManager):
    """Класс для работы с данными в JSON файлах"""

    def __init__(self, filename: str = "vacancies.json"):
        self.filename = filename
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Создание файла если он не существует"""
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def add_vacancy(self, vacancy: Dict[str, Any]) -> None:
        """Добавление вакансии в файл"""
        vacancies = self._load_all_vacancies()
        vacancies.append(vacancy)
        self._save_all_vacancies(vacancies)

    def add_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """Добавление списка вакансий в файл"""
        existing_vacancies = self._load_all_vacancies()
        existing_vacancies.extend(vacancies)
        self._save_all_vacancies(existing_vacancies)

    def get_vacancies(self, criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Получение вакансий по критериям"""
        vacancies = self._load_all_vacancies()

        if not criteria:
            return vacancies

        filtered_vacancies = []
        for vacancy in vacancies:
            matches = True
            for key, value in criteria.items():
                if key not in vacancy or vacancy[key] != value:
                    matches = False
                    break
            if matches:
                filtered_vacancies.append(vacancy)

        return filtered_vacancies

    def delete_vacancy(self, criteria: Dict[str, Any]) -> None:
        """Удаление вакансий по критериям"""
        vacancies = self._load_all_vacancies()
        filtered_vacancies = []

        for vacancy in vacancies:
            matches = True
            for key, value in criteria.items():
                if key not in vacancy or vacancy[key] != value:
                    matches = False
                    break
            if not matches:
                filtered_vacancies.append(vacancy)

        self._save_all_vacancies(filtered_vacancies)

    def _load_all_vacancies(self) -> List[Dict[str, Any]]:
        """Загрузка всех вакансий из файла"""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_all_vacancies(self, vacancies: List[Dict[str, Any]]) -> None:
        """Сохранение всех вакансий в файл"""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(vacancies, f, ensure_ascii=False, indent=2)

    def clear_all_vacancies(self) -> None:
        """Очистка всех вакансий"""
        self._save_all_vacancies([])
