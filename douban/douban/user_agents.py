from random import randint, choice


def user_agent():
    chrome_version = 'Chrome/{}.0.{}.{}'.format(
        randint(55, 62), randint(0, 3200), randint(0, 140))

    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)',
        '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]

    return ' '.join(
        [
            'Mozilla/5.0',
            choice(os_type),
            'AppleWebKit/537.36',
            '(KHTML, like Gecko)',
            chrome_version,
            'Safari/537.36'
        ]
    )
