website_configs = {
    'website1': {
        'url': 'https://www.x.com/api',
        'method': 'POST',
        'send_as_json': False,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'send_with_headers': True,
        'headers': {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
            },
        'success': 'registered',
        'failure': 'Failed to send'
    },
    'website2': {
        'url': 'https://www.x.com/api',
        'method': 'POST',
        'send_as_json': False,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'msisdn': f'{phone_number}'},
        'payload': {},
        'send_with_headers': False,
        'headers': {},
        'success': '0',
        'failure': 'false'
    },
    'website3': {
        'url': 'https://www.x.com/api',
        'method': 'POST',
        'send_as_json': True,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {
            'Main': {
                'firstname': f'{first_name}',
               'lastname': f'{last_name}',
                'Email': f'{gmail}',
                'Password': 'dfDD123A',
                'ReceiveCampaignMessages': 'True',
                'GenderID': '4',
                'CellPhone': f'{phone_number}'
            }
        },
        'send_with_headers': True,
        'headers': {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
            },
        'payload': {},    
        'success': 'origin',
        'failure': 'Method Not Allowed'
    },
    'website4': {
        'url': 'http://httpbin.org/ip',
        'method': 'POST',
        'send_as_json': False,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'send_with_headers': False,
        'headers': {},
        'success': 'origin',
        'failure': 'Method Not Allowed'
    }
}
