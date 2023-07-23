import re
import requests
import os
import urllib3
import chardet
import json
import concurrent.futures
from colorama import Fore, init
from sms import send_sms_requests
from titlescreen import print_title_screen

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
init(autoreset=True)

current_version = '1.0.0'

def get_latest_version(url):
    try:
        response = requests.get(url)
        latest_version = response.text.strip()
    except Exception:
        return False
    return latest_version

def is_valid_number(number, country_code):
    if country_code == "TR":
        pattern = r'^\d{10}$'
    else:
        pattern = r'^\d{7,11}$'
    return (re.match(pattern, number))

def validate_phone_numbers(phone_numbers, country_code):
    valid_numbers = []
    invalid_numbers = []

    for number in phone_numbers:
        if is_valid_number(number, country_code):
            valid_numbers.append(number)
        else:
            invalid_numbers.append(number)

    return valid_numbers, invalid_numbers

def get_country_code():
    while True:
        country_code = input(f"{Fore.MAGENTA}Enter target country code. Example 'US': {Fore.RESET}").lower()
        with open('country_codes.json', 'r') as f:
            data = json.load(f)
            country_code = country_code.upper()
            if country_code in data:
                return country_code, data[country_code]
            else:
             print(f"{Fore.RED}Country code is not found. Please try again.{Fore.RESET}")


def check_config_file(country_code):
    file_name = f"websiteconfigs/website_config_{country_code}.py"
    if os.path.isfile(file_name):
        return file_name
    else:
        print(f"{Fore.RED}Error: {file_name.lower()} not found. Quiting.{Fore.RESET}")
        return False

def get_phone_number_or_file(country_code, area_code):
    while True:
        choice = input(f"{Fore.MAGENTA}Enter (1) to input phone number or (2) to provide a file path: {Fore.RESET}").lower()
        if choice == '1':
            return get_phone_number(country_code, area_code), None
        elif choice == '2':
            return None, get_file_path()
        else:
            print(f"{Fore.RED}Invalid choice. Please enter '1' or '2'.{Fore.RESET}")

def get_phone_number(country_code, area_code):
    while True:
        number = input(f"{Fore.MAGENTA}Enter the target phone number (without +{area_code}) or press Enter to import from a file: {Fore.RESET}").lower()
        if not number:
            return None
        if is_valid_number(number, country_code):
            return number
        else:
            print(f"{Fore.RED}Invalid Turkish phone number. Please try again or press Enter to import from a file.{Fore.RESET}")

def get_file_path(prompt=f"{Fore.MAGENTA}Enter the file path of the .txt file: {Fore.RESET}"):
    while True:
        file_path = input(prompt)
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            return file_path
        else:
            print(f"{Fore.RED}Invalid file path or format. Please enter a valid .txt file.{Fore.RESET}")

def get_proxy_choice():
    while True:
        choice = input(f"{Fore.MAGENTA}Would you like to use a proxy? (y/n): {Fore.RESET}").lower()
        if choice == 'y':
            return 'y'
        elif choice == 'n':
            return None
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 'y' or 'n'.{Fore.RESET}")

def is_valid_proxy(proxy):
    pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})(:(\w+):(\w+))?$")
    if re.match(pattern, proxy):
        return True
    return False

def validate_proxies(proxies):
    valid_proxies = []
    invalid_proxies = []

    for proxy in proxies:
        if is_valid_proxy(proxy):
            valid_proxies.append(proxy)
        else:
            invalid_proxies.append(proxy)

    return valid_proxies, invalid_proxies

def get_proxy_or_file():
    while True:
        choice = input(f"{Fore.MAGENTA}Enter (1) to input proxy details or (2) to provide a file path: {Fore.RESET}").lower()

        if choice == '1':
            proxies = get_proxy_details()
            if proxies:  # Check if list is not empty
                return proxies
            print(f"{Fore.RED}Invalid proxy details. Please try again.{Fore.RESET}")

        elif choice == '2':
            file_path = get_file_path(f"{Fore.MAGENTA}Enter the file path of the .txt file containing the proxy details: {Fore.RESET}")
            if file_path is not None:
                try:
                    proxies = read_file(file_path)
                except Exception as e:
                  print(f"{Fore.RED}Unable to read proxy file path. Please make sure file only includes proxies. Quiting.")
                  print(f"Exception: {e}")
                  return  
                if proxies is not None and len(proxies) > 0:
                    return proxies
                print(f"{Fore.RED}No valid proxies found in the provided file. Please try again.{Fore.RESET}")

        else:
            print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.{Fore.RESET}")

def get_proxy_details():
    proxies = []
    while True:
        proxy = input(f"{Fore.MAGENTA}Enter your proxy credentials in the following format - (ip:port or ip:port:user:password):{Fore.RESET}")
        if is_valid_proxy(proxy):
            # Only use the ip:port or ip:port:user:password part for the actual proxy
            proxy = proxy.split()[0]
            proxies.append(proxy)
            return proxies  # Return just the list of proxies
        else:
            print(f"{Fore.RED}Invalid proxy credentials. Please try again.{Fore.RESET}")

def get_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def read_file(file_path):
    if not file_path or not os.path.isfile(file_path):
        print(f"{Fore.RED}Invalid file path. Please try again.{Fore.RESET}")
        return []
    encoding = get_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as f:
        items = [line.strip().split()[0] for line in f.readlines() if line.strip()]
    items = list(set(items))  # Remove duplicates
    return items

def test_proxy(proxy, developer_mode=False):
    test_http_url = 'http://httpbin.org/ip'
    test_https_url = 'https://api.myip.com/'
    proxy_results = {'http': False, 'https': False}

    try:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            ip, port, username, password = proxy_parts
            proxy_url = f'http://{username}:{password}@{ip}:{port}'
        else:
            ip, port = proxy_parts
            proxy_url = f'http://{ip}:{port}'
        proxies = {'http': proxy_url, 'https': proxy_url}

        # Test HTTP
        response_http = requests.get(test_http_url, proxies=proxies, timeout=50)
        proxy_results['http'] = response_http.status_code == 200

        # Test HTTPS
        response_https = requests.get(test_https_url, proxies=proxies, timeout=50)
        proxy_results['https'] = response_https.status_code == 200

    except Exception as e:
        if developer_mode:
            print(f"{Fore.RED}Error testing proxy '{proxy}': {e}{Fore.RESET}") 

    return proxy_results

def get_max_workers(proxies):
    return min(len(proxies), 5000)

def test_proxies_and_show_results(proxies, developer_mode=False):
    successful_proxies = []
    unsuccessful_proxies = []
    tested_proxies_count = 0
    successful_proxies_count = 0
    unsuccessful_proxies_count = 0

    print(f"{Fore.CYAN}Testing proxies...{Fore.RESET}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=get_max_workers(proxies)) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy, developer_mode): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                proxy_results = future.result()
            except Exception as exc:
                print(f"{Fore.RED}Error testing proxy '{proxy}': {exc}{Fore.RESET}")
                continue

            tested_proxies_count += 1
            if proxy_results['http'] or proxy_results['https']:
                proxy_parts = proxy.split(':')
                if len(proxy_parts) == 4:
                    ip, port, username, password = proxy_parts
                else:
                    ip, port = proxy_parts

                if proxy_results['http']:
                    protocol = 'http'
                    proxy_url = f'{protocol}://{username}:{password}@{ip}:{port}' if len(proxy_parts) == 4 else f'{protocol}://{ip}:{port}'
                    successful_proxies.append(proxy_url)
                if proxy_results['https']:
                    protocol = 'https'
                    proxy_url = f'{protocol}://{username}:{password}@{ip}:{port}' if len(proxy_parts) == 4 else f'{protocol}://{ip}:{port}'
                    successful_proxies.append(proxy_url)

                successful_proxies_count += 1
                if proxy_results['http'] and proxy_results['https']:
                    print(f'{Fore.GREEN}{proxy.split(":")[0]} HTTP/HTTPS{Fore.RESET}')
                elif proxy_results['http']:
                    print(f'{Fore.GREEN}{proxy.split(":")[0]} HTTP{Fore.RESET}')
                else: 
                    print(f'{Fore.GREEN}{proxy.split(":")[0]} HTTPS{Fore.RESET}')
            else:
                print(f'{Fore.RED}{proxy.split(":")[0]}{Fore.RESET}')
                unsuccessful_proxies.append(proxy)
                unsuccessful_proxies_count += 1
    http_proxies = [proxy for proxy in successful_proxies if proxy.startswith('http://')]
    https_proxies = [proxy for proxy in successful_proxies if proxy.startswith('https://')]
    print(f"{Fore.GREEN}HTTP proxies: {len(http_proxies)}")
    print(f"{Fore.GREEN}HTTPS proxies: {len(https_proxies)}")
    print(f"{Fore.CYAN}Tested proxies: {tested_proxies_count}")
    #print(f"{Fore.GREEN}Successful proxies: {successful_proxies_count}")
    print(f"{Fore.RED}Unsuccessful proxies: {unsuccessful_proxies_count}{Fore.RESET}")

    return successful_proxies, http_proxies, https_proxies

def main():
    print_title_screen()

    print (r"""[ ! ] For authorized testing only. Use responsibly with explicit permission. Developer not responsible for illegal use.
           """)
    
    url = "https://raw.githubusercontent.com/farukalpay/SMS-Sender/main/version.txt"
    latest_version = get_latest_version(url)
    if latest_version and current_version != latest_version:
            print (Fore.RED + r"""[ ! ] The version you are using is outdated. Continuing to use this version may lead to errors. 
https://github.com/farukalpay/SMS-Sender
                   """)
    
    country_code, area_code = get_country_code()
    filename = check_config_file(country_code) 
    if filename is False:
        return

    phone_number, file_path = get_phone_number_or_file(country_code, area_code)
    if file_path:
        phone_numbers = read_file(file_path)
        if phone_numbers is None:
            return
        valid_phone_numbers, invalid_phone_numbers = validate_phone_numbers(phone_numbers, country_code)
        if len(valid_phone_numbers) == 0:
            print(f"{Fore.RED}No valid phone numbers found in the provided file. Quitting.{Fore.RESET}")
            return
        phone_numbers = valid_phone_numbers
    elif phone_number:
        phone_numbers = [phone_number]
    else:
        print(f"{Fore.RED}No valid input provided. Quitting.{Fore.RESET}")
        return

    use_proxy = get_proxy_choice()
    if use_proxy:
        proxy = get_proxy_or_file()
        if proxy is None:
            return
        valid_proxies, invalid_proxies = validate_proxies(proxy)
        if len(valid_proxies) == 0:
            print(f"{Fore.RED}No valid proxies found. Quitting.{Fore.RESET}")
            return
        proxies = valid_proxies

        successful_proxies, http_proxies, https_proxies = test_proxies_and_show_results(proxies)
        if len(successful_proxies) == 0:
            print(f"{Fore.RED}No successful proxies. Quitting.{Fore.RESET}")
            return
    else:
        http_proxies = []
        https_proxies = []

    while True:
        send_sms_choice = input(f"{Fore.MAGENTA}Do you want to start sending SMS? (y/n): {Fore.RESET}").lower()
        if send_sms_choice == 'y':
            developer_mode = False
            break
        elif send_sms_choice == 'developer':
            developer_mode = True
            break
        elif send_sms_choice == 'n':
            print(f"{Fore.RED}SMS sending process terminated.{Fore.RESET}")
            return
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 'y' or 'n'.{Fore.RESET}")

    print_title_screen()
    send_sms_requests(phone_numbers, http_proxies, https_proxies, filename, developer_mode)

if __name__ == "__main__":
    main()