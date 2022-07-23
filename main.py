"""
A Script to retrieve grades from a html page
"""
import json
import logging
import os
import mechanicalsoup as ms

import requests


def open_grade_page():
    """
    Opens the grade page and returns the browser
    :return: the browser object
    """
    # create a browser object
    browser = ms.StatefulBrowser()
    # login to the website by using the form
    browser.open(url)
    browser.select_form('form[name="loginform"]')
    browser['asdf'] = username
    browser['fdsa'] = password
    browser.submit_selected()
    logging.debug('Logged in')
    # navigate to the grades page
    browser.follow_link(text='Prüfungsverwaltung')
    browser.follow_link(text='HTML-Ansicht Ihrer erbrachten Leistungen')
    browser.follow_link(text='Abschluss Bachelor of Science')
    grade_link = browser.get_current_page().find_all('a', title='Leistungen für Informatik  anzeigen')[0]
    browser.follow_link(grade_link)
    logging.debug('Navigated to grades page')

    return browser


def retrieve_grades(browser):
    """
    Retrieves the grades from the page and returns them as a dict
    :param browser: the browser object
    :return: the grades as a dict
    """

    # get the grades from the table
    table = browser.get_current_page().find_all('table')[1]
    # parse the table
    grade_dict = {}
    for row in table.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 0:
            lecture = cols[1].text.strip()
            grade = cols[3].text.strip()
            if len(grade) > 0 and grade != '0,0':
                grade_dict[lecture] = grade

    return grade_dict


def check_for_update(grades):
    """
    Checks if there is a new grade and updates the savefile if there is
    :param grades: the grades as a dict
    :return: True if there is a new grade, False otherwise
    """
    # check if there is a new grade
    new_grade = False
    file = 'grades.json'
    new_grades = {}

    # if file exists
    if os.path.isfile(file):
        logging.debug('File exists')
        with open(file, 'r') as f:
            old_grades = json.load(f)
        for lecture in grades.keys():
            if lecture not in old_grades.keys():
                new_grade = True
                new_grades[lecture] = grades[lecture]
                logging.debug(f'New grade for {lecture}')
    else:
        logging.debug('File does not exist')
        new_grade = True
    if new_grade:
        logging.debug('Write new grades to file')
        with open(file, 'w') as f:
            json.dump(grades, f)
    return new_grade, new_grades


def notify(new_grades, bot_token, bot_chat_id):
    # build message in HTML format
    message = '<b>Neue Prüfungen:</b>\n\n'
    for lecture in new_grades.keys():
        message += '<u>' + lecture + '</u>:\t<b>' + new_grades[lecture] + '</b>\n'
    logging.debug(f'Telegram-Message: {message}')
    # send message to telegram bot
    response = requests.post(
        'https://api.telegram.org/bot' + bot_token + '/sendMessage',
        data={'chat_id': bot_chat_id, 'text': message, 'parse_mode': 'HTML'})

    if response.status_code != 200:
        logging.error(f'Error sending message!\n{response.text}')
    else:
        logging.info('Message sent!')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting...')

    # load environment variables
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    url = os.environ['URL']

    # load bot token and chat id
    chat_id = os.environ['CHAT_ID']
    token = os.environ['BOT_TOKEN']

    logging.info('Logging in...')
    browser = open_grade_page()

    logging.info('Retrieving grades...')
    grade_dict = retrieve_grades(browser)

    logging.info('Checking for update...')
    is_update, new_grades = check_for_update(grade_dict)
    if is_update:
        logging.info('New grade found!')
        notify(new_grades, token, chat_id)
    else:
        logging.info('No new grade found.')
