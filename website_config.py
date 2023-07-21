website_configs = {
    'website1': {
        'url': 'http://www.website.com/users/registration/',
        'method': 'POST',
        'send_as_json': False,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'first_name': f'{first_name}', 'last_name': f'{last_name}', 'email': f'{gmail}', 'password': 'cactusboy1234', 'confirm': 'true', 'kvkk': 'true', 'phone': f'0{phone_number}'},
        'payload': {},
        'send_with_headers': False,
        'headers': {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
            },
        'send_with_cookies': False,
        'cookies': {},
        'response_base': 'status', #text for text based, status for html status code based.
        'status_code': ['200', '201', '202', '203', '204'],
        'success': 'registered',
        'failure': ['0', '1', 'true']
    },
    'website2': {
        'url': 'http://www.website.com/users/registration/',
        'method': 'GET',
        'send_as_json': False,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'msisdn': f'{phone_number}'},
        'payload': {},
        'send_with_headers': False,
        'headers': {},
        'send_with_cookies': False,
        'cookies': {},
        'response_base': 'status',
        'status_code': ['200', '201', '202', '203', '204'],
        'success': ['0', '1', 'true'],
        'failure': 'false'
    },
    'website3': {
        'url': 'http://www.website.com/users/registration/',
        'method': 'GET',
        'send_as_json': False,
        'payload_function': lambda first_name, last_name, gmail, phone_number: {'phone': f'{phone_number}', 'companyID': '1'},
        'payload': {},
        'send_with_headers': False,
        'headers': {},
        'send_with_cookies': False,
        'cookies': {},
        'response_base': 'status',
        'status_code': ['200', '201', '202', '203', '204'],
        'success': 'Value cannot be null',
        'failure': {}
    }
}