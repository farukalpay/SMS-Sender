website_configs = {
    'web1': {
        'url': 'https://www.web1.com/',
        'method': 'POST',
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'success': 'registered',
        'failure': 'Failed to send'
    },
    'web2': {
        'url': 'https://api.web2.com/',
        'method': 'GET',
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'msisdn': f'{phone_number}'},
        'payload': {},
        'success': 'origin',
        'failure': 'false'
    },
    'web3': {
        'url': 'http://httpbin.org/ip',
        'method': 'GET',
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'success': 'origin',
        'failure': 'Method Not Allowed'
    }
}