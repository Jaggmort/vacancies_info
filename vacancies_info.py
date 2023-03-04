import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def main():
    load_dotenv()
    superjob_api_key = os.environ.get('SUPERJOB_KEY')
    professions = ['JavaScript',
                   'Java',
                   'Python',
                   'Ruby',
                   'PHP',
                   'C++',
                   'C#',
                   'Go',
                   'Objective-C',
                   'Scala',
                   'Swift'
                   ]
    headhunter_title = 'HeadHunter Moscow'
    superjob_title = 'SuperJob Moscow'
    print()
    superjob_vacancies = get_superjob_vacancies(superjob_api_key, professions)
    show_table(superjob_title, superjob_vacancies)
    print()
    headhunter_vacancies = get_headhunter_vacancies(professions)
    show_table(headhunter_title, headhunter_vacancies)


def calculate_wage(payment_from, payment_to):
    wage = None
    if (not payment_from):
        if payment_to:
            wage = int(payment_to*0.8)
        return wage        
    if payment_to:
        wage = int(payment_from + payment_to)/2
    else:
        wage = int(payment_from*1.2)
    return wage


def predict_salary(salary):
    wage = None
    if salary:
        if salary['currency'] == 'rub':
            wage = calculate_wage(salary['payment_from'], salary['payment_to'])
        if salary['currency'] == 'RUR':
            wage = calculate_wage(salary['from'], salary['to'])
    return wage


def show_table(title, wages):
    header = ['Язык программирования',
              'Вакансий найдено',
              'Вакансий обработано',
              'Средняя зарплата'
              ]
    wages.insert(0, header)
    table_instance = AsciiTable(wages, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)
    return None


def get_headhunter_vacancies(professions):
    url = 'https://api.hh.ru/vacancies'
    professions_vacancies = []
    for profession in professions:
        page = 0
        pages_number = 1
        suitable_vacancies = 0
        wages_sum = 0
        while page < pages_number:
            params = {'text': f'Программист {profession}', 'page': page}
            page_response = requests.get(url, params)
            page_response.raise_for_status()
            page_payload = page_response.json()
            pages_number = page_payload['pages']
            page += 1
            for vacancy in page_payload['items']:
                salary = predict_salary(vacancy['salary'])
                if salary:
                    suitable_vacancies += 1
                    wages_sum += salary
        try:
            average_wages = int(wages_sum/suitable_vacancies)
        except ZeroDivisionError:
            average_wages = None
        profession_vacancies = [
            profession,
            page_payload['found'],
            suitable_vacancies,
            average_wages
        ]
        professions_vacancies.append(profession_vacancies)
    return professions_vacancies


def get_superjob_vacancies(api_key, professions):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': api_key}
    professions_vacancies = []
    moscow_id = 4
    for profession in professions:
        vacancies = 0
        suitable_vacancies = 0
        page = 0
        wages_sum = 0
        more = True
        while more:
            params = {'town': moscow_id, 'keyword': profession, 'page': page}
            page_response = requests.get(url, headers=headers, params=params)
            page_response.raise_for_status()
            page_payload = page_response.json()
            more = page_payload['more']
            vacancies = page_payload['total']
            page += 1
            for vacancy in page_payload['objects']:
                salary = predict_salary(vacancy)
                if salary:
                    suitable_vacancies += 1
                    wages_sum += salary
        try:
            average_wages = int(wages_sum/suitable_vacancies)
        except ZeroDivisionError:
            average_wages = None
        profession_vacancies = [
            profession,
            vacancies,
            suitable_vacancies,
            average_wages
        ]
        professions_vacancies.append(profession_vacancies)
    return professions_vacancies


if __name__ == '__main__':
    main()
