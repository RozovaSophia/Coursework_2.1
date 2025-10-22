from src.data_manager import *


def user_interaction():
    """Функция для взаимодействия с пользователем через консоль"""

    # Инициализация компонентов
    hh_api = HeadHunterAPI()
    data_manager = JSONDataManager()

    print("=== Парсер вакансий HeadHunter ===")

    while True:
        print("\n" + "=" * 50)
        print("1. Поиск вакансий на HeadHunter")
        print("2. Показать топ N вакансий по зарплате")
        print("3. Поиск вакансий по ключевому слову в описании")
        print("4. Показать все сохраненные вакансии")
        print("5. Очистить все вакансии")
        print("0. Выход")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            search_query = input("Введите поисковый запрос: ").strip()
            if not search_query:
                print("Запрос не может быть пустым!")
                continue

            print("Загружаем вакансии...")
            vacancies_data = hh_api.get_vacancies(search_query, per_page=50)

            if vacancies_data:
                # Преобразуем в объекты Vacancy и сохраняем
                vacancies_objects = [Vacancy.from_dict(data) for data in vacancies_data]
                data_manager.add_vacancies([vac.to_dict() for vac in vacancies_objects])
                print(f"Загружено и сохранено {len(vacancies_objects)} вакансий")
            else:
                print("Не удалось загрузить вакансии")

        elif choice == "2":
            try:
                n = int(input("Введите количество вакансий для показа: "))
                all_vacancies_data = data_manager.get_vacancies()
                vacancies = [Vacancy.from_dict(data) for data in all_vacancies_data]

                # Фильтруем вакансии с зарплатой и сортируем
                vacancies_with_salary = [v for v in vacancies if v.salary_from > 0 or v.salary_to > 0]
                sorted_vacancies = sorted(vacancies_with_salary, reverse=True)[:n]

                if sorted_vacancies:
                    print(f"\nТоп-{n} вакансий по зарплате:")
                    for i, vacancy in enumerate(sorted_vacancies, 1):
                        print(f"{i}. {vacancy}")
                else:
                    print("Нет вакансий с указанной зарплатой")

            except ValueError:
                print("Пожалуйста, введите корректное число")

        elif choice == "3":
            keyword = input("Введите ключевое слово для поиска в описании: ").strip()
            if not keyword:
                print("Ключевое слово не может быть пустым!")
                continue

            all_vacancies_data = data_manager.get_vacancies()
            vacancies = [Vacancy.from_dict(data) for data in all_vacancies_data]

            filtered_vacancies = [v for v in vacancies if v.has_keyword_in_requirement(keyword)]

            if filtered_vacancies:
                print(f"\nНайдено {len(filtered_vacancies)} вакансий с ключевым словом '{keyword}':")
                for i, vacancy in enumerate(filtered_vacancies, 1):
                    print(f"{i}. {vacancy}")
            else:
                print(f"Вакансий с ключевым словом '{keyword}' не найдено")

        elif choice == "4":
            all_vacancies_data = data_manager.get_vacancies()
            vacancies = [Vacancy.from_dict(data) for data in all_vacancies_data]

            if vacancies:
                print(f"\nВсе сохраненные вакансии ({len(vacancies)}):")
                for i, vacancy in enumerate(vacancies, 1):
                    print(f"{i}. {vacancy}")
            else:
                print("Нет сохраненных вакансий")

        elif choice == "5":
            confirm = input("Вы уверены, что хотите очистить все вакансии? (y/n): ")
            if confirm.lower() == "y":
                data_manager.clear_all_vacancies()
                print("Все вакансии очищены")

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор, попробуйте снова")


if __name__ == "__main__":
    user_interaction()
