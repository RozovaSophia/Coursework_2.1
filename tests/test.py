import unittest
from unittest.mock import Mock, patch

from src.data_manager import *


class TestVacancy(unittest.TestCase):

    def setUp(self):
        self.vacancy_data = {
            "name": "Python Developer",
            "url": "https://hh.ru/vacancy/123",
            "salary_from": 100000,
            "salary_to": 150000,
            "employer": "Test Company",
            "requirement": "Python, Django, Flask",
        }

    def test_vacancy_creation(self):
        vacancy = Vacancy(**self.vacancy_data)
        self.assertEqual(vacancy.name, "Python Developer")
        self.assertEqual(vacancy.salary_from, 100000)
        self.assertEqual(vacancy.salary_to, 150000)

    def test_vacancy_validation(self):
        with self.assertRaises(ValueError):
            Vacancy("", "https://test.com", 100000, 150000)

        with self.assertRaises(ValueError):
            Vacancy("Test", "", 100000, 150000)

    def test_vacancy_comparison(self):
        vac1 = Vacancy("Job1", "url1", 100000, 150000)
        vac2 = Vacancy("Job2", "url2", 80000, 120000)
        vac3 = Vacancy("Job3", "url3", 100000, 150000)

        self.assertTrue(vac1 > vac2)
        self.assertTrue(vac1 >= vac3)
        self.assertTrue(vac1 == vac3)
        self.assertTrue(vac2 < vac1)


class TestHeadHunterAPI(unittest.TestCase):

    def setUp(self):
        self.api = HeadHunterAPI()

    @patch("requests.Session.get")
    def test_connect_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.api.connect()
        self.assertTrue(result)

    @patch("requests.Session.get")
    def test_get_vacancies(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "1",
                    "name": "Python Developer",
                    "alternate_url": "https://hh.ru/vacancy/1",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
                    "employer": {"name": "Test Company"},
                    "snippet": {"requirement": "Python experience"},
                    "experience": {"name": "1-3 years"},
                    "published_at": "2024-01-01",
                }
            ]
        }
        mock_get.return_value = mock_response

        vacancies = self.api.get_vacancies("Python")
        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["name"], "Python Developer")


class TestJSONDataManager(unittest.TestCase):

    def setUp(self):
        self.test_filename = "test_vacancies.json"
        self.manager = JSONDataManager(self.test_filename)
        self.sample_vacancy = {
            "name": "Test Job",
            "url": "https://test.com",
            "salary_from": 100000,
            "salary_to": 150000,
            "employer": "Test Company",
            "requirement": "Test requirements",
        }

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_add_and_get_vacancy(self):
        self.manager.add_vacancy(self.sample_vacancy)
        vacancies = self.manager.get_vacancies()

        self.assertEqual(len(vacancies), 1)
        self.assertEqual(vacancies[0]["name"], "Test Job")

    def test_delete_vacancy(self):
        self.manager.add_vacancy(self.sample_vacancy)
        self.manager.delete_vacancy({"name": "Test Job"})

        vacancies = self.manager.get_vacancies()
        self.assertEqual(len(vacancies), 0)


if __name__ == "__main__":
    unittest.main()
