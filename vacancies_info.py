import requests
from terminaltables import AsciiTable


def predict_rur_salary(salary):
    if salary is None:
        return None
    wage = None
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
    if salary is None:
        return None
    wage = None
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


def headhunter_vacancies_info():
    url_all = 'https://api.hh.ru/vacancies'
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
    full_info = []
    profession_info = []
    for profession in professions:
        page = 0
        pages_number = 1
        vacancies_fit = 0
        wages_sum = 0
        while page < pages_number:
            params = {'text': f'Программист {profession}', 'page': page}
            page_response = requests.get(url_all, params)
            page_response.raise_for_status()
            page_payload = page_response.json()
            pages_number = page_payload['pages']
            page += 1
            for item in page_payload['items']:
                if predict_rur_salary(item['salary']):
                    vacancies_fit += 1
                    wages_sum += predict_rur_salary(item['salary'])
        try:
            wages_average = int(wages_sum/vacancies_fit)
        except ZeroDivisionError:
            wages_average = None
        profession_info.append(profession)
        profession_info.append(page_payload['found'])
        profession_info.append(vacancies_fit)
        profession_info.append(wages_average)
        full_info.append(profession_info)
        profession_info = []
        title = 'HeadHunter Moscow'
    show_table(title, full_info)
    return None


def superjob_vacancies_info():
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {'X-Api-App-Id': 'v3.r.137397509.4016b29888ab574f2cb1f31d74e0ddb333fade59.4c5446fd495394f76992b88010cc84cbc0cdc91e'}
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
    full_info = []
    profession_info = []
    for profession in professions:
        vacancies_fit = 0
        page = 0
        wages_sum = 0
        more = True
        while more:
            params = {'town': 4, 'keyword': f'Программист {profession}', 'page': page}
            page_response = requests.get(url, headers=headers, params=params)
            page_response.raise_for_status()
            page_payload = page_response.json()
            more = page_payload['more']
            page += 1
            for item in page_payload['objects']:
                if predict_rub_salary(item):
                    vacancies_fit += 1
                    wages_sum += predict_rub_salary(item)
        try:
            wages_average = int(wages_sum/vacancies_fit)
        except ZeroDivisionError:
            wages_average = None
        profession_info.append(profession)
        profession_info.append(page_payload['total'])
        profession_info.append(vacancies_fit)
        profession_info.append(wages_average)
        full_info.append(profession_info)
        profession_info = []
    title = 'SuperJob Moscow'
    show_table(title, full_info)


if __name__ == '__main__':
    print()
    superjob_vacancies_info()
    print()
    headhunter_vacancies_info()