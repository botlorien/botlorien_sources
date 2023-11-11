from setuptools import setup, find_packages

setup(
    name="botlorien_sources",
    version="1.0.2",
    packages=find_packages(),
    description='Main source classes for BotLórien RPA Development',
    author='Ben-Hur P. B. Santos',
    author_email='botlorien@gmail.com',
    install_requires=[
        'selenium',
        'webdriver-manager',
        'beautifulSoup4',
        'customtkinter',
        'Pillow',
        'psycopg2',
        'cryptography',
        'pandas',
        'openpyxl',
        'gspread',
        'oauth2client',
        'tkcalendar',
        'pyppeteer',
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'msedge-selenium-tools'
        ],
    )

# python setup.py sdist
