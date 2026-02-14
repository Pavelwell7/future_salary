import requests

from environs import Env
from terminaltables import AsciiTable
from itertools import count


def predict_rub_salary_hh(vacancy):
    if  vacancy['salary'] is None or vacancy['salary']['currency'] != 'RUR':
        return None
    if vacancy['salary']['from'] and vacancy['salary']['to']:
        return  (vacancy['salary']['to'] + vacancy['salary']['from'])/2
    elif vacancy['salary']['from']:
        return vacancy['salary']['from'] * 1.2
    elif vacancy['salary']['to']:
        return vacancy['salary']['to'] * 0.8
    return None

def get_language_statistic_hh(url, language):
    search_field = f'Программист {language}'
    payload = {
        'text': search_field,
        'area': 1,
        'per_page': 100,
    }
    headers = {
        'User-Agent': 'curl/7.74.0',
        'Accept-Language': 'ru-RU'
    }
    vacancies_found = 0
    vacancies_processed = 0
    total_salary = 0
    for page in count(0):
        payload['page'] = page
        page_response = requests.get(url, params=payload, headers=headers)
        page_response.raise_for_status()
        vacancies = page_response.json()
        if page == 0:
            vacancies_found = vacancies['found']
        for vacancy in vacancies['items']:
            predicted_salary = predict_rub_salary_hh(vacancy)
            if predicted_salary:
                total_salary += predicted_salary
                vacancies_processed += 1
        if page >= vacancies['pages']:
            break
    if vacancies_processed>0:
        average_salary = int(total_salary / vacancies_processed)
    else:
        average_salary = 0
    return{
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    if not salary_from and not salary_to:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8

    return None

def get_language_statistic_sj(url, language, token):
    search_field = f'Программист {language}'
    payload = {
        'keyword': search_field,
        'town': 4,
        'count': 100,
        'page': 0,
    }
    headers = {
        'User-Agent': 'curl/7.74.0',
        'Accept-Language': 'ru-RU',
        'X-Api-App-Id': token,
    }
    vacancies_found = 0
    vacancies_processed = 0
    total_salary = 0
    for page in count(0):
        payload['page'] = page
        page_response = requests.get(url, params=payload, headers=headers)
        page_response.raise_for_status()
        vacancies = page_response.json()
        if page == 0:
            vacancies_found = vacancies['total']
        for vacancy in vacancies['objects']:
            predicted_salary = predict_rub_salary_sj(vacancy)
            if predicted_salary:
                total_salary += predicted_salary
                vacancies_processed += 1
        if page >= vacancies['more']:
            break
    if vacancies_processed>0:
        average_salary = int(total_salary / vacancies_processed)
    else:
        average_salary = 0
    return{
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }

def main():

    env = Env()
    env.read_env()

    url_hh = env('HH_URL')
    url_sj = env('SJ_URL')
    token = env('TOKEN')

    languages = [
        'Python',
        'SQL',
        'javascript',
        'java',
        'php',
        'c#',
        'c',
        'c++',
        'go',
    ]
    table_hh = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    for lang in languages:
        stats_hh = get_language_statistic_hh(url_hh, lang)
        table_hh.append([
            lang,
            stats_hh['vacancies_found'],
            stats_hh['vacancies_processed'],
            stats_hh['average_salary'],
        ])
    table_sj = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата',
    ]]
    table_ascii_hh = AsciiTable(table_hh)
    table_ascii_hh.title = 'HeadHunter Moscow'
    print(table_ascii_hh.table)

    for lang in languages:
        stats = get_language_statistic_sj(url_sj, lang, token)
        table_sj.append([
            lang,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary'],
        ])
    table_ascii_sj = AsciiTable(table_sj)
    table_ascii_sj.title = 'SuperJob Moscow'
    print(table_ascii_sj.table)

if __name__ == '__main__':
    main()

