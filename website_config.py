website_configs = {
    'x': {
        'url': 'https://www.x/users/registration/',
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'success': 'registered',
        'failure': 'Failed to send'
    },
    'website2': {
        'url': 'http://x.org/ip',
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'success': 'origin',
        'failure': 'Method Not Allowed'
    }
}