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
    get_superjob_vacancies(superjob_api_key, professions)
    get_headhunter_vacancies(professions)


def predict_rur_salary(salary):
    wage = None
    if salary:
        if salary['currency'] == 'RUR':
            if salary['from']:
                if salary['to']:
                    wage = int((salary['from'] + salary['to'])/2)
                else:
                    wage = int(salary['from']*1.2)
            else:
                if salary['to']:
                    wage = int(salary['to']*0.8)
                else:
                    wage = None
    return wage


def predict_rub_salary(salary):
    wage = None
    if salary:
        if salary['currency'] == 'rub':
            if salary['payment_from']:
                if salary['payment_to']:
                    wage = int((salary['payment_from'] + salary['payment_to'])/2)
                else:
                    wage = int(salary['payment_from']*1.2)
            else:
                if salary['payment_to']:
                    wage = int(salary['payment_to']*0.8)
                else:
                    wage = None
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
    title = 'HeadHunter Moscow'    
    url = 'https://api.hh.ru/vacancies'
    overall_result = []
    profession_result = []
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
                predict_salary = predict_rur_salary(vacancy['salary'])
                if predict_salary:
                    suitable_vacancies += 1
                    wages_sum += predict_salary
        try:
            wages_average = int(wages_sum/suitable_vacancies)
        except ZeroDivisionError:
            wages_average = None
        profession_result.append(profession)
        profession_result.append(page_payload['found'])
        profession_result.append(suitable_vacancies)
        profession_result.append(wages_average)
        overall_result.append(profession_result)
        profession_result = []
    print()
    show_table(title, overall_result)
    return None


def get_superjob_vacancies(api_key, professions):
    title = 'SuperJob Moscow'
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': api_key}
    overall_result = []
    profession_result = []
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
                predict_salary = predict_rub_salary(vacancy)
                if predict_salary:
                    suitable_vacancies += 1
                    wages_sum += predict_salary
        try:
            wages_average = int(wages_sum/suitable_vacancies)
        except ZeroDivisionError:
            wages_average = None
        profession_result.append(profession)
        profession_result.append(vacancies)
        profession_result.append(suitable_vacancies)
        profession_result.append(wages_average)
        overall_result.append(profession_result)
        profession_result = []
    print()
    show_table(title, overall_result)


if __name__ == '__main__':
    main()
