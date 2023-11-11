# importações
import logging
import os
import time
# import pyautogui
# import pyperclip
from pathlib import Path

import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from subprocess import CREATE_NO_WINDOW  # This flag will only be available in windows
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert
import random
import urllib.parse
import threading as td
from functools import partial


#
class WhatsApp:
    """
    A class to interact with WhatsApp web.

    :param caminho: (str) The path where downloaded files will be saved. Defaults to 'downloads'.

    :return: None

    Example:
        >>>whats = WhatsApp()
    """

    class TimeoutException(Exception):
        pass

    def __init__(self, caminho: str = 'downloads'):
        """
        Initialize a WhatsApp object.

        :param caminho: (str) The path where downloaded files will be saved. Defaults to 'downloads'.

        :return: None
        """
        self._criar_pastas('parameters')
        self.caminho = os.path.abspath(os.getcwd() + '/' + caminho)
        self.driver = None
        self.action = None
        self.initialized_whats = False
        self.home_chat = self._criar_arquivo_txt('#Home_api_Bot@', 'home_chat', 'parameters')
        self.number = self._criar_arquivo_txt('+55.....', 'self_number', 'parameters')
        # self.init_browser()

    def _criar_pastas(self, path):
        """
        This function creates a new folder in the specified path, if it does not exist.

        :param path: (str) A string with the path to the folder to be created.
        :return: (str) The absolute path of the created folder.

        Example:
            To create a new folder named "data" in the current working directory:

            >>> criar_pastas('data')
            '/path/to/current/working/directory/data'
        """
        if not ':' in path:
            root_path = os.getcwd()
            path = os.path.abspath(root_path + f'/{path}')

        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def _criar_arquivo_txt(self, text: str = '', name_file: str = '', path_to_save: str = '', subs: bool = False):
        """
        Create a new text file or open an existing one and return its content.

        :param text: (str) Text to write to the file. Default is an empty string.
        :param name_file: (str) The name of the file to be created or opened.
        :param path_to_save: (str) The path to the folder where the file will be created or opened. Default is the current working directory.
        :param subs: (bool) If True, the text in the file will be replaced by the new text. If False and the file exists, the existing text will be returned. Default is False.

        :return: (str) The content of the file.
        """
        path_to_save = self._criar_pastas(path_to_save)
        full_path_file = f'{path_to_save}\{name_file}.txt'

        if not os.path.exists(full_path_file) or subs:
            with open(full_path_file, 'w') as f:
                f.write(text)
        else:
            with open(full_path_file, 'r') as f:
                text = f.read()
        return text

    def init_browser(self, name_instance: str = 'Default'):
        """
        Initializes a Chrome browser instance with customized settings and options.

        :param name_instance: (str) The name of the user profile to be used. Defaults to 'Default'.
        :return: None

        Example:
            To initialize a browser instance with a specific user profile:
            >> init_browser('my_profile')
        """
        path_chrome_driver = self._criar_pastas('path_chromedriver')
        appdata_path = os.getenv('APPDATA')  # Get the path to the current user's AppData directory
        appdata_dir = os.path.dirname(appdata_path)  # Get the directory name of the AppData directory
        path_store_profile = os.path.abspath(appdata_dir + '/Local/profile_chrome')
        _ = self._criar_pastas(path_store_profile)
        path_store_profile = os.path.abspath(appdata_dir + f'/Local/profile_chrome/{name_instance}')
        path_store_profile = self._criar_pastas(path_store_profile)
        print(path_store_profile)

        profile_path = os.path.abspath(path_store_profile + '/Default')
        print(profile_path)
        profile_path = self._criar_arquivo_txt(profile_path, 'profile_path_whatsapp', 'parameters')

        options = Options()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")  # optional
        options.add_argument("--disable-popup-blocking")  # optional
        options.add_argument("--disable-extensions")  # optional

        options.add_experimental_option("prefs", {
            "download.default_directory": self.caminho,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
            # Disable Chrome's PDF Viewer
            "download.extensions_to_open": "applications/pdf",
            'plugins.always_open_pdf_externally': True
        })

        # Trying to use ChromeDriverManager to get the latest driver
        try:
            chrome_service = Service(ChromeDriverManager().install())
        except:
            # If fails, use the existing local driver
            print('Tentando com chromedriver local...')
            chrome_service = Service("chromedriver.exe")

        if len(profile_path) > 0:
            options.add_argument(f"user-data-dir={profile_path}")
            # options.add_argument('headless')
            self.driver = webdriver.Chrome(service=chrome_service, options=options)
            self.action = ActionChains(self.driver)
        else:
            options.add_argument(f"user-data-dir={path_store_profile}")
            driver = webdriver.Chrome(service=chrome_service, options=options)
            driver.get("chrome://version/")
            script = 'var path = document.getElementById("profile_path").innerText;return path'
            profile_path = driver.execute_script(script)
            profile_path = self._criar_arquivo_txt(profile_path, 'profile_path', 'parameters', True)
            print(profile_path)
            options.add_argument(f"user-data-dir={profile_path}")
            self.driver = webdriver.Chrome(service=chrome_service, options=options)
            self.action = ActionChains(self.driver)

    def _time_out(void=None, time_out: int = 20, raise_exception: bool = False):
        """
        Executes a function with a timeout limit.

        :param void: (optional) Default argument, unused.
        :type void: any
        :param time_out: The timeout limit in seconds.
        :type time_out: int
        :param raise_exception: (optional) If True, a TimeoutException will be raised when the timeout is reached.
        :type raise_exception: bool
        :return: Returns the result of the executed function.
        :rtype: any

        Example:
            This decorator can be used to set a timeout limit for a function that takes too long to execute.
            >>>@_time_out(time_out=30, raise_exception=True)
            >>>def slow_function():
            >>>    time.sleep(35)
            >>>
            >>>slow_function()
            TimeoutException: Timeout!
        """

        def wrapper(func):
            def inner_wrapper(*args, **kwargs):
                print("Time out value: {}".format(time_out))
                contador_time_out = 0
                ret = False
                while contador_time_out < time_out:
                    try:
                        ret = func(*args, **kwargs)
                        break
                    except Exception as e:
                        logging.exception(e)
                        time.sleep(1)
                    contador_time_out += 1
                if contador_time_out > time_out and raise_exception:
                    raise WhatsApp.TimeoutException("Timeout!")
                return ret

            return inner_wrapper

        return wrapper

    @_time_out()
    def _find_qrcode(self):
        """
        Waits for the QR code to be available on the screen, finds and extracts its value.

        :return: (str) The QR code value.

        This method waits for the QR code to be available on the screen by waiting for a canvas element to be clickable. Once the element is available, it extracts the QR code value by running a JavaScript code on the browser. The extracted QR code value is then returned as a string.

        Example:
        >>> qr_code_value = self._find_qrcode()
        """
        WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.TAG_NAME, 'canvas')))

        script = """
        var element = document.querySelectorAll('div[data-testid="qrcode"]');
        return element
        """
        element = self.driver.execute_script(script)
        qrcode = element[0].get_attribute('data-ref')
        print(qrcode)
        time.sleep(1)

    @_time_out(time_out=5)
    def open_whats(self):
        """
        Opens a WhatsApp chat window by navigating to the WhatsApp web page and entering the phone number and message.
        If there is an active instance of WhatsApp, it opens the home chat. If there is no active instance, it waits for the user to access by scanning the QR code.

        :return: None

        :raises Exception: If fails to start WhatsApp after the QR code scanning

        :Example:
            To open WhatsApp and send a message to a phone number:
            >>> wp = WhatsApp()
            >>> wp.open_whats()
            >>> wp.search('John')
            >>> wp.send_msg('Hi John, how are you?')
        """
        # self.driver.get('https://web.whatsapp.com/')
        self.driver.get(f"https://web.whatsapp.com/send?phone={self.number}&text=''")
        # Verifica se whatsApp já tem uma instancia ativa
        if not self.search('', enter=False) == True:
            # Esperando pelo usuario acessar com o qrcode
            self._find_qrcode()
            if not self.search('', enter=False) == True:
                self.driver.quit()
                raise Exception('Falha em iniciar o WhatsApp!')
            else:
                self.initialized_whats = True
                _ = self.search(self.home_chat)
                self._click_close_search()

        else:
            self.initialized_whats = True
            _ = self.search(self.home_chat)
            self._click_close_search()

    @_time_out(time_out=3)
    def _disable_alerts(self):
        """
        Disables any alerts that appear on the page.
        :return: None
        """
        alert = Alert(self.driver)
        alert.accept()

    @_time_out()
    def _click_button_send_msg(self):
        """
        The _click_button_send_msg method clicks the "Send" button on the WhatsApp chat window to send a message to the current chat.
        :return: None
        """
        script = """
        document.querySelectorAll('span[data-icon="send"]')[0].click()
        """
        self.driver.execute_script(script)
        time.sleep(1)

    @_time_out()
    def send_msg_to_number(self, msg, phone_no, path_file: str = ''):
        """
        Sends a message to a given phone number on WhatsApp Web.

        :param msg: (str) Message to send.
        :param phone_no: (str) Phone number to send the message to, in international format without '+' or '00' prefixes.
        :param path_file: (str) Path to a file to be sent along with the message.
        :return: None

        Example:
            >>> whatsapp = WhatsApp()
            >>> whatsapp.open_whats()
            >>> whatsapp.send_msg_to_number("Hello, world!", "1234567890")
        """
        link = f"https://web.whatsapp.com/send?phone={phone_no}"
        self.driver.get(link)
        self._disable_alerts()
        self._write_conversation_box(msg)
        self._click_button_send_msg()
        if len(str(path_file)) > 0 and ':' in str(path_file):
            self.send_file(path_file)
        #_ = self.search(self.home_chat)
        #self._click_close_search()

    @_time_out()
    def _write_conversation_box(self, msg):
        """
        Writes a message to the conversation box in the WhatsApp Web interface.

        :param msg: (str) Message to be written to the conversation box.
        :return: None

        Example:
            >>> _write_conversation_box('Hello, how are you?')
        """
        script = """
        var element = document.querySelectorAll('p[class="selectable-text copyable-text iq0m558w g0rxnol2"]')[1]
        element.focus();
        return element
        """
        msg = pyperclip.copy(msg)
        # document.execCommand('insertText', false, '{msg}');
        element = self.driver.execute_script(script)
        element.send_keys(Keys.DELETE)
        self.action.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

    def send_msg_to_contact(self, msg, contact, path_file: str = ''):
        """
        Sends a message to a specific contact.

        :param msg: (str) The message to be sent.
        :param contact: (str) The name of the contact to send the message.
        :param path_file: (str) The path to the file to be sent (if any).

        :return: None.

        Example:
            To send a message to a contact named "John Doe":

            >>> send_msg_to_contact("Hello John, how are you?", "John Doe")
        """
        self.search(contact)
        self._write_conversation_box(msg)
        self._click_button_send_msg()
        if len(str(path_file)) > 0 and ':' in str(path_file):
            self.send_file(path_file)

        _ = self.search(self.home_chat)
        self._click_close_search()

    @_time_out(time_out=30)
    def search(self, valor, enter: bool = True):
        """
        Searches for a chat or contact on WhatsApp Web and enters the chat if found.

        :param valor: (str) The name or phone number of the chat or contact to search for.
        :param enter: (bool) Whether to press Enter after typing the search query. Default is True.
        :return: (bool) True if the search was successful, False otherwise.

        Example:
            >>> search("John")
            True
        """
        script = """
        var element = document.querySelectorAll('p[class="selectable-text copyable-text iq0m558w g0rxnol2"]')[0]
        return element
        """
        element = self.driver.execute_script(script)

        if enter:
            element.click()
            self.action.key_down(Keys.CONTROL).send_keys('A').key_up(Keys.CONTROL).perform()
            element.send_keys(Keys.DELETE)
            element.send_keys(valor, Keys.ENTER)
        return True

    @_time_out()
    def _click_clip(self):
        """
        Clicks on the clip icon to open the attachment options.
        """
        script = """
        document.querySelectorAll('span[data-icon="attach-menu-plus"]')[0].click();return 0;
        """
        self.driver.execute_script(script)

    @_time_out()
    def _append_file(self, path_file):
        """
        Attaches a file to the message input box.

        :param path_file: str - path to the file to be attached
        """
        script = """
           var elemento = document.querySelectorAll('li[class="jScby Iaqxu FCS6Q _2UNQo"]')[0];
           var elemento2 = elemento.querySelectorAll("input[type=file]")[0];
           return elemento2;
           """
        elemento = self.driver.execute_script(script)
        elemento.send_keys(path_file)
        time.sleep(2)

    @_time_out()
    def _append_img(self, path_file):
        """
        Attaches an image to the message input box.

        :param path_file: str - path to the image to be attached
        """
        script = """
           var elemento = document.querySelectorAll('button[aria-label="Fotos e vídeos"]')[0];
           var elemento2 = document.querySelectorAll("input[type=file]")[2];
           return elemento2;
           """
        elemento = self.driver.execute_script(script)
        elemento.send_keys(path_file)
        time.sleep(2)

    @_time_out()
    def _click_button_send_file(self):
        """
        Clicks on the send button after the file has been attached.
        """
        script = """
        document.querySelectorAll('div[aria-label="Enviar"]')[0].click()
        """
        self.driver.execute_script(script)

    def send_file(self, path_file):
        self._click_clip()

        if not '.png' in str(path_file).lower() and not '.jpg' in str(path_file).lower() and not '.jpeg' in str(
                path_file).lower():
            self._append_file(path_file)
        else:
            self._append_img(path_file)

        self._click_button_send_file()

    @_time_out()
    def _check_msg_sent(self):
        """
        This function checks if the message is sent or not.

        :return: (None): No return value.

        Example:
            >>> _check_msg_sent()
        """
        script = """
        var elements = document.querySelectorAll('span[data-testid="msg-check"]')
        return elements
        """
        elements = self.driver.execute_script(script)

    @_time_out()
    def _get_all_msg_sent(self):
        """
        This function gets all the sent messages.

        :return: (list): List of messages that are sent.

        Example:
            >>> _get_all_msg_sent()
        """
        script = """
        var elements = document.querySelectorAll('div[class="ItfyB _3nbHh"]')
        return elements
        """
        elements = self.driver.execute_script(script)
        for element in elements:
            print('#' * 50)
            print(element.text)
        list_value = [str(element.text) for element in elements]
        return list_value

    @_time_out()
    def _get_content_conversation(self, mode: str = 'all'):
        """
            This method gets the content of a conversation with a specific contact in WhatsApp.

            :param mode: (str) "all" to get all messages in the conversation or "last_content" to get only the last message sent
            :return: (list) A list of strings containing the text of the messages
            :raises: TimeoutException if the page takes too long to load

            Example:
                >>> _get_content_conversation('all')
                ['Hello, how are you?', 'I am doing well, thanks for asking!', 'How about you?']
        """
        self._scroll_panel_conversation('bottom')
        elements = []
        if mode == 'last_content':
            script = """
            document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('div[class="hY_ET"]');
            });
            var elements = document.querySelectorAll('div[class="hY_ET"]');
            return elements
            """
            elements = self.driver.execute_script(script)
        elif mode == 'all':
            _, elements = self._scroll_panel_conversation('top')
        print(elements[0])
        for element in elements[0]:
            print('#' * 50)
            print(element.text)
        list_value = [str(element.text) for element in elements[0]]
        print(list_value)
        return list_value

    @_time_out()
    def get_contents_from_contact(self, contact):
        """
        This method get_contents_from_contact searches for a contact in WhatsApp and retrieves the conversation history with that contact. It uses the _get_content_conversation method to retrieve the content of the conversation, and waits for the content to be loaded up to 3 times if necessary.

        :param contact: (str) name or phone number of the contact to search for
        :return: (list) conversation history with the contact, represented as a list of strings
        """
        self.search(contact)
        values = []
        count = 0
        while not len(values) > 1 and count < 3:
            values = self._get_content_conversation()
            time.sleep(1)
            count += 1
        return values

    @_time_out()
    def _scroll_panel_conversation(self, mode):
        """
            This function scrolls through the conversation panel messages and returns its contents based on the mode selected.

            :param mode: (str) 'top' or 'bottom' value to select the direction of the scrolling.
            :return: (tuple) scroll_element and contents based on the mode selected.
            :raises: Exception if scroll does not complete after three attempts.

            Example:
                >>> self._scroll_panel_conversation('top')
                (<selenium.webdriver.remote.webelement.WebElement object at 0x7fdd3b4f04c0>,
                 [ [<selenium.webdriver.remote.webelement.WebElement object at 0x7fdd3b4f00d0>, ... ]
        """
        # Scroll to top
        if mode == 'top':
            script = """
            function scrollToTop() {
              document.addEventListener('DOMContentLoaded', function() {
                document.querySelectorAll('div[class="hY_ET"]');
              });

              var contents = [];
              const element = document.querySelector('div[data-testid="conversation-panel-messages"]');
              if (element.scrollTop > 0) {
                window.requestAnimationFrame(scrollToTop);
                element.scrollTop -= element.scrollTop / (element.scrollTop/10); // Adjust this value to change the scrolling speed

                //Optional script

                contents.push(document.querySelectorAll('div[class="hY_ET"]'))

                }

              return contents
            }
            var contents = scrollToTop()
            return contents
            """
        # Scroll to bottom
        else:
            script = """
            const element = document.querySelector('div[data-testid="conversation-panel-messages"]');
            element.scrollTo(0,element.scrollHeight);

            document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('div[class="hY_ET"]');
            });
            var contents = [];
            contents.push(document.querySelectorAll('div[class="hY_ET"]'));
            return contents
            """
        contents = self.driver.execute_script(script)

        script = """
        const element = document.querySelector('div[data-testid="conversation-panel-messages"]');
        return element
        """
        scroll_element = self.driver.execute_script(script)

        return scroll_element, contents

    @_time_out()
    def get_chats(self):
        """
            Returns a list of all chats.

            :process: This method executes JavaScript on the page to retrieve all chats from the chat list panel.
            :return: A list containing all chats found in the chat list panel.

            Example:
                To get all chats, use:
                >>> get_chats()
                ["Chat 1", "Chat 2", "Chat 3", ...]
        """
        script = """
        var element = document.querySelectorAll('div[data-testid="chat-list"]');
        return element
        """
        chats = self.driver.execute_script(script)
        print(chats)
        print('#' * 50)
        for chat in chats:
            print('-' * 50)
            print(chat.text)
        print('#' * 50)
        print('Individual')
        script = """
        var element = document.querySelectorAll('div[data-testid="cell-frame-container"]');
        return element
        """
        chats = self.driver.execute_script(script)
        print(chats)
        for chat in chats:
            print('-' * 50)
            print(chat.text)
            print('#' * 50)

    @_time_out()
    def get_unread_chat(self):
        """
            Finds the first unread chat in the WhatsApp web application and clicks on it to open the chat window.
            Returns the text of the unread messages.

            :return: (str) Text of the unread messages.

            This method performs the following steps:
            1. Executes a JavaScript code to find all the elements containing unread messages.
            2. Clicks on the first element with unread messages.
            3. Returns the text of the unread messages.

            Example:
            To get the text of the first unread message:
            >>> driver = webdriver.Chrome()
            >>> whatsapp = WhatsApp(driver)
            >>> text = whatsapp.get_unread_chat()
        """
        script = """
        var elements = document.querySelectorAll('span[data-testid="icon-unread-count"]')
        var parentElements = [];

        for (var i = 0; i < elements.length; i++) {
          parentElements.push(elements[i].closest('div[class="_8nE1Y"]'));
        }
        return parentElements
        """
        unreads = self.driver.execute_script(script)
        print(len(unreads))
        print(unreads)
        values = []
        if unreads is not None:
            unread = [unread for unread in unreads if unread is not None]
            if len(unread) > 0:
                unread = unread[0]
                values = str(unread.text)
                print(values)
                self.action.move_to_element(unread).perform()
                unread.click()
                if len(values) > 0:
                    _ = self.search(self.home_chat)
                    self._click_close_search()

        return values

    @_time_out()
    def get_unreads_chat(self):
        """
            Returns the number of unread chats and opens them, if any.

            :return: A list of strings with the number of unread messages of each chat
            :rtype: list

            This function gets all the elements with the `data-testid` attribute set to "icon-unread-count",
            and finds their parent elements with the class "_8nE1Y". It then returns a list of the parent elements.

            If there are any unread chats, this function clicks on each one of them to open the chat.

            Once all unread chats are opened, the function returns a list of strings with the number of unread
            messages of each chat.

            Example:
                >>> get_unreads_chat()
                2
                [<selenium.webdriver.remote.webelement.WebElement (session="...", element="...")>,
                 <selenium.webdriver.remote.webelement.WebElement (session="...", element="...")>]
                ['3', '2']
        """
        script = """
            var elements = document.querySelectorAll('span[data-testid="icon-unread-count"]')
            var parentElements = [];

            for (var i = 0; i < elements.length; i++) {
              parentElements.push(elements[i].closest('div[class="_8nE1Y"]'));
            }
            return parentElements
            """
        unreads = self.driver.execute_script(script)
        print(len(unreads))
        print(unreads)
        if unreads is not None:
            values = [str(unread.text) for unread in unreads if unread is not None]
            unreads = [unread for unread in unreads if unread is not None]
            for unread in unreads:
                print(unread.text)
                self.action.move_to_element(unread).perform()
                unread.click()
            if len(values) > 0:
                _ = self.search(self.home_chat)
                self._click_close_search()

        return values

    @_time_out(time_out=3)
    def _click_close_search(self):
        """
        This method clicks on the close search button.

        :return: None
        """
        script = """
        document.querySelectorAll('span[data-icon="x-alt"]')[0].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def _get_last_contents(self):
        """
        This method gets the last contents from the chat.

        :return: List of web elements
        """
        script = """
        var elements = document.querySelectorAll('div[data-testid="msg-container"]')
        return elements
        """
        contents = self.driver.execute_script(script)
        return contents

    @_time_out()
    def get_last_content_from_contact(self, contact):
        """
        This method gets the last content from a contact.

        :param contact: Contact name
        :return: List of strings
        """
        self.search(contact)
        self._scroll_panel_conversation('bottom')
        time.sleep(3)
        contents = self._get_last_contents()
        values = [str(content.text) for content in contents]
        for content in contents:
            print('-' * 50)
            print(content.text)
        _ = self.search(self.home_chat)
        self._click_close_search()

        return values

    @_time_out()
    def _forward_media_chat(self):
        """
        Find all the HTML div elements with an aria-label attribute set to "Encaminhar arquivo de mídia"
        (Forward Media File in English) and click on each of them.

        :returns: None
        """
        script = """
        var elements = document.querySelectorAll('div[aria-label="Encaminhar arquivo de mídia"]')
        return elements
        """
        contents = self.driver.execute_script(script)
        for content in contents:
            content.click()

    @_time_out()
    def _click_forward_msg(self):
        """
        Find the first HTML span element with a data-testid attribute set to "forward"
        and click on it.

        :returns: None
        """
        script = """
        document.querySelectorAll('span[data-testid="forward"')[0].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def _search_contact_forward_msg(self, to_contact):
        """
        Find the HTML paragraph element with a class attribute set to "selectable-text copyable-text iq0m558w"
        and enter the given contact name into it. Then, wait for 3 seconds and press the Enter key.

        :param to_contact: A string representing the name of the contact to forward the message to.
        :type to_contact: str
        :returns: None
        """
        list_contacts = to_contact.split(';')
        for to_contact in list_contacts:
            script = f"""
            var element = document.querySelectorAll('p[class="selectable-text copyable-text iq0m558w"]')[0]
            return element
            """
            element = self.driver.execute_script(script)
            element.send_keys(to_contact)
            time.sleep(3)
            element.send_keys(Keys.ENTER)
            self.action.key_down(Keys.CONTROL).send_keys('A').key_up(Keys.CONTROL).perform()
            element.send_keys(Keys.DELETE)

    @_time_out()
    def _click_send_forward_msg(self):
        """
        Find the first HTML span element with a data-testid attribute set to "send" and click on it using
        the execute_script() method.

        :returns: None
        """
        script = """
            document.querySelectorAll('span[data-testid="send"]')[0].click()
            """
        self.driver.execute_script(script)

    @_time_out()
    def _click_on_msg_forward(self):
        """
        Find the HTML span element with a data-testid attribute set to "down-context" and click on it.
        Then, find the first HTML list item element with a data-testid attribute set to "mi-msg-forward"
        and click on it using the execute_script() method.

        :returns: None
        """
        script = """
        document.querySelectorAll('span[data-testid="down-context"]')[0].click()
        document.querySelectorAll('li[data-testid="mi-msg-forward"]')[0].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def forward_last_msg_from_contact(self, from_contact, to_contact):
        """
        The forward_last_msg_from_contact method forwards the last message from a given contact to another contact.

        :param from_contact: the name of the contact to forward the message from.
        :type from_contact: str
        :param to_contact: the name of the contact to forward the message to.
        :type to_contact: str

        :return: None

        This method first searches for the conversation with the given from_contact and scrolls to the bottom of the conversation to get the last message contents. Then it moves the mouse pointer to the last message and clicks on the "forward" button. It then clicks on the "forward" button on the popup menu and enters the to_contact in the search bar. Finally, it clicks on the "send" button to forward the message to the to_contact.
        """
        self.search(from_contact)
        self._scroll_panel_conversation('bottom')
        time.sleep(3)
        contents = self._get_last_contents()
        self.action.move_to_element(contents[-1]).perform()
        self._click_on_msg_forward()
        self._click_forward_msg()
        self._search_contact_forward_msg(to_contact)
        time.sleep(3)
        self._click_send_forward_msg()

    @_time_out()
    def _click_download_media(self):
        """
        Clicks on the download button for a media file in the user's chat.

        :process: The function executes a JavaScript script that locates the first element with an 'aria-label' attribute set
                  to 'Baixar' (which means 'Download' in Portuguese) and clicks on it. This is typically the download button
                  for the media file that is currently selected in the user's chat.
        :return: None.

        Example:
            To download the media file that is currently selected in the user's chat, call the function like this:

            >>> _click_download_media()
        """
        script = """
        document.querySelectorAll('div[aria-label="Baixar"]')[0].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def _click_close_media(self):
        """
        Clicks on the close button for the media viewer.

        :process: The function executes a JavaScript script that locates the first element with a 'data-testid' attribute set
                  to 'x-viewer' and clicks on it. This is typically the close button for the media viewer that is currently
                  displayed on the user's screen.
        :return: None.

        Example:
            To close the media viewer, call the function like this:

            >>> _click_close_media()
        """
        script = """
        document.querySelectorAll('span[data-testid="x-viewer"]')[0].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def _find_media_imgs(self):
        """
        Finds all media images in the user's chat.

        :process: The function executes a JavaScript script that locates all elements with a 'data-testid' attribute set to
                  'media-url-provider'. These elements typically contain the URLs for media images that are displayed in the
                  user's chat.
        :return: A list of WebElement objects that represent the media images found in the user's chat.

        Example:
            To find all media images in the user's chat, call the function like this:

            >>> medias = _find_media_imgs()
        """
        script = """
        var elements = document.querySelectorAll('div[data-testid="media-url-provider"]')
        return elements
        """
        medias = self.driver.execute_script(script)
        return medias

    @_time_out()
    def _find_media_documents(self):
        """
        Finds all media documents in the user's chat.

        :process: The function executes a JavaScript script that locates all elements with a 'data-testid' attribute set to
                  'document-thumb'. These elements typically represent media documents that are displayed in the user's chat.
        :return: A list of WebElement objects that represent the media documents found in the user's chat.

        Example:
            To find all media documents in the user's chat, call the function like this:

            >>> medias = _find_media_documents()
        """
        script = """
        var elements = document.querySelectorAll('button[data-testid="document-thumb"]')
        return elements
        """
        medias = self.driver.execute_script(script)
        return medias

    @_time_out()
    def download_last_medias_from_contact(self, contact):
        """
        Downloads the last media files received from a given contact.

        :process: The function searches for the given contact and scrolls the conversation panel to the bottom to load all
                  messages. It then finds all media images and documents in the conversation and downloads them by clicking
                  the download button and then closing the media viewer. The function does not return anything.

        :param contact: The name or phone number of the contact whose media files should be downloaded.
        :type contact: str

        Example:
            To download the last media files received from a contact named 'John Doe', call the function like this:

            >>> download_last_medias_from_contact('John Doe')
        """
        self.search(contact)
        self._scroll_panel_conversation('bottom')
        medias = self._find_media_imgs()
        if medias is not None:
            for media in medias:
                media.click()
                self._click_download_media()
                self._click_close_media()
        medias = self._find_media_documents()
        if medias is not None:
            for media in medias:
                media.click()

    @_time_out()
    def _click_menu_info_contact(self):
        """
        Clicks on the contact menu and selects the option to view contact information.

        :process: Navigates to the contact menu and selects the "Chat Info" option.
        :return: None
        """
        script = """
        document.querySelectorAll('span[data-testid="menu"]')[1].click()
        document.querySelectorAll('li[data-testid="menu-item-chat-info"]')[0].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def _get_info_contacts(self):
        """
        Obtains information about the current WhatsApp contact.

        :process: Queries the HTML document for elements containing contact information.
        :return: A list of HTML elements containing contact information.
        """
        script = """
        var elements = document.querySelectorAll('div[class="lhggkp7q ln8gz9je rx9719la"]')
        return elements
        """
        elements = self.driver.execute_script(script)
        return elements

    @_time_out()
    def _get_info_participants(self):
        script = """
        var elements = document.querySelectorAll('div[data-testid="cell-frame-container"]')
        return elements
        """
        elements = self.driver.execute_script(script)
        return elements

    @_time_out()
    def _click_search_participants_contact(self):
        """
        Clicks the "Search participants and contacts" button on the current web page.

        :process: Uses JavaScript to locate the button element on the page and clicks it.
        :return: None

        Example:
            # create an instance of the class containing the method
            my_object = MyClass()

            # call the method to click the button
            my_object._click_search_participants_contact()
        """
        script = """
        document.querySelectorAll('span[data-testid="search"]')[1].click()
        """
        self.driver.execute_script(script)

    @_time_out()
    def _scroll_list_participants(self, times):
        full_content = []
        for i in range(times):
            script = f"""
            var painel = document.querySelectorAll('div[data-testid="contacts-modal"]')[0].children[2]
            var len = painel.scrollHeight/{times}
            painel.scrollTo(0,len*{i})
            """
            self.driver.execute_script(script)

            @self._time_out()
            def _contents():
                elements = self._get_info_participants()
                contents = [str(element.text) for element in elements]
                return contents

            contents = _contents()

            if contents:
                full_content += contents

        return full_content

    @_time_out()
    def get_info_from_contact(self, contact):
        """
        Retrieves information about a contact from the current web page.

        :param contact: A string representing the name of the contact to retrieve information about.
        :process: Uses other methods from the class to search for the contact, click on the "Info" menu item, and retrieve information from the page.
        :return: A list of strings representing the information about the contact.

        Example:
            # create an instance of the class containing the method
            my_object = MyClass()

            # call the method to retrieve information about a contact
            info = my_object.get_info_from_contact("John Smith")

            # print the information
            print(info)
        """
        self.search(contact)
        self._click_menu_info_contact()
        self._click_search_participants_contact()
        contents = self._scroll_list_participants(100)
        print(contents)
        return contents


if __name__ == '__main__':
    pass
