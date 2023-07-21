import re
import requests
import os
import urllib3
import chardet
from colorama import Fore, init
from sms import send_sms_requests
from titlescreen import print_title_screen


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
init(autoreset=True)

def is_valid_turkish_number(number):
    pattern = r'^\d{10}$'
    return re.match(pattern, number)

def validate_phone_numbers(phone_numbers):
    valid_numbers = []
    invalid_numbers = []

    for number in phone_numbers:
        if is_valid_turkish_number(number):
            valid_numbers.append(number)
        else:
            invalid_numbers.append(number)

    return valid_numbers, invalid_numbers

def get_phone_number_or_file():
    while True:
        choice = input(f"{Fore.MAGENTA}Enter (1) to input phone number or (2) to provide a file path: {Fore.RESET}").lower()
        if choice == '1':
            return get_phone_number(), None
        elif choice == '2':
            return None, get_file_path()
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.{Fore.RESET}")

def get_phone_number():
    while True:
        number = input(f"{Fore.MAGENTA}Enter the target phone number (without +90) or press Enter to import from a file: {Fore.RESET}").lower()
        if not number:
            return None
        if is_valid_turkish_number(number):
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
    choice = input(f"{Fore.MAGENTA}Would you like to use a proxy? (y/n): {Fore.RESET}").lower()
    return choice == 'y'

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
    test_url = 'http://httpbin.org/ip'
    try:
        proxy_parts = proxy.split(':')
        if len(proxy_parts) == 4:
            ip, port, username, password = proxy_parts
            proxy_url = f'http://{username}:{password}@{ip}:{port}'
        else:
            ip, port = proxy_parts
            proxy_url = f'http://{ip}:{port}'
        proxies = {'http': proxy_url}
        response = requests.get(test_url, proxies=proxies, timeout=50)
        return response.status_code == 200
    except Exception as e:
        if developer_mode:
            print(f"{Fore.RED}Error testing proxy '{proxy}': {e}{Fore.RESET}") 
        return False

def test_proxies_and_show_results(proxies, developer_mode=False):
    successful_proxies = []
    unsuccessful_proxies = []
    tested_proxies_count = 0
    successful_proxies_count = 0
    unsuccessful_proxies_count = 0

    print(f"{Fore.CYAN}Testing proxies...{Fore.RESET}")

    for proxy in proxies:
        is_successful = test_proxy(proxy, developer_mode)
        tested_proxies_count += 1
        if is_successful:
            successful_proxies.append(proxy)
            successful_proxies_count += 1
            print(f'{Fore.GREEN}{proxy.split(":")[0]} - SUCCESS{Fore.RESET}')
        else:
            unsuccessful_proxies.append(proxy)
            unsuccessful_proxies_count += 1
            print(f'{Fore.RED}{proxy.split(":")[0]} - FAILED{Fore.RESET}')

    print(f"{Fore.CYAN}Tested proxies: {tested_proxies_count}")
    print(f"{Fore.GREEN}Successful proxies: {successful_proxies_count}")
    print(f"{Fore.RED}Unsuccessful proxies: {unsuccessful_proxies_count}{Fore.RESET}")

    return successful_proxies, unsuccessful_proxies

def main():
    print_title_screen()
    
    print (r"""[ ! ] For authorized testing only. Use responsibly with explicit permission. Developer not responsible for illegal use.
           """)

    phone_number, file_path = get_phone_number_or_file()
    if file_path:
        phone_numbers = read_file(file_path)
        if phone_numbers is None:
            return
        valid_phone_numbers, invalid_phone_numbers = validate_phone_numbers(phone_numbers)
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
    else:
        proxies = []

    test_proxies = input(f"{Fore.MAGENTA}Would you like to test proxies? (y/n): {Fore.RESET}").lower()
    if test_proxies == 'y':
        successful_proxies, unsuccessful_proxies = test_proxies_and_show_results(proxies)
        if len(successful_proxies) == 0:
            print(f"{Fore.RED}No successful proxies. Quitting.{Fore.RESET}")
            return
        proxies = successful_proxies

    send_sms_choice = input(f"{Fore.MAGENTA}Do you want to start sending SMS? (y/n): {Fore.RESET}").lower()

    if send_sms_choice == 'y':
        developer_mode = False
    elif send_sms_choice == 'developer':
        developer_mode = True
    else:
        print(f"{Fore.YELLOW}SMS sending process terminated.{Fore.RESET}")
        return

    print_title_screen()
    send_sms_requests(phone_numbers, proxies, developer_mode)

if __name__ == "__main__":
    main()