from setuptools import setup, find_packages

setup(
    name="priority_classes",
    version="0.30",
    packages=find_packages(),
    description='Priority Classes Package for carvalima bots',
    author='Ben-Hur P. B. Santos',
    author_email='benstronics@gmail.com',
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
