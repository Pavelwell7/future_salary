from itertools import count

from environs import Env
import requests
from terminaltables import AsciiTable


def predict_rub_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 0.8

def predict_rub_salary_hh(vacancy):
    if  vacancy['salary'] is None or vacancy['salary']['currency'] != 'RUR':
        return None
    salary_from = vacancy['salary']['from']
    salary_to = vacancy['salary']['to']
    return predict_rub_salary(salary_from, salary_to)

def get_language_statistic_hh(language):

    url_hh = 'https://api.hh.ru/vacancies'

    search_field = f'Программист {language}'
    moscow = 1
    pages = 100
    payload = {
        'text': search_field,
        'area': moscow,
        'per_page': pages,
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
        page_response = requests.get(url_hh, params=payload, headers=headers)
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
    if vacancies_processed:
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
    return predict_rub_salary(salary_from, salary_to)

def get_language_statistic_sj(language, token):
    url_sj = 'https://api.superjob.ru/2.0/vacancies'
    search_field = f'Программист {language}'
    moscow = 4
    pages = 100
    payload = {
        'keyword': search_field,
        'town': moscow,
        'count': pages,
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
        page_response = requests.get(url_sj, params=payload, headers=headers)
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
    if vacancies_processed:
        average_salary = int(total_salary / vacancies_processed)
    else:
        average_salary = 0
    return{
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary,
    }


def get_statistics(languages, stats_function):
    results = []
    for lang in languages:
        stats = stats_function(lang)
        results.append((lang, stats))
    return results


def make_table(title, languages_statistics):
    table_data = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]

    for language, stats in languages_statistics:
        table_data.append([
            language,
            stats['vacancies_found'],
            stats['vacancies_processed'],
            stats['average_salary'],
        ])

    ascii_table = AsciiTable(table_data)
    ascii_table.title = title
    return ascii_table.table


def main():
    env = Env()
    env.read_env()
    token_sj = env('TOKEN_SJ')

    languages = [
        'Python', 'SQL', 'javascript', 'java',
        'php', 'c#', 'c', 'c++', 'go',
    ]

    hh_languages = get_statistics(languages, get_language_statistic_hh)
    print(make_table('HeadHunter Moscow', hh_languages))

    sj_languages = get_statistics(languages, lambda lang: get_language_statistic_sj(lang, token_sj))
    print(make_table('SuperJob Moscow', sj_languages))


if __name__ == '__main__':
    main()

